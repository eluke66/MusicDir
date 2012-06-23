#!/usr/bin/env python

from Tkinter import *
import re

def cleanup():
    root.quit()

class Separator(Frame):
    def __init__(self,parent,horizontal=True,borderWidth=2):
        Frame.__init__( self, parent, bd=borderWidth, relief=RIDGE, height=2,pady=50)

#######################################
class Dialog(Toplevel):

    def __init__(self, parent, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override

#######################################
class EntryDialog(Dialog):
    def __init__(self, parent, table, title = None):
        self.table = table
        Dialog.__init__(self,parent,title)
        
    def body(self, master):
        f = Frame(master)
        row = 0
        self.NewEntries = []
        for col in config.getEntryCols(self.table):
            label = Label(f, text=col)
            label.grid(row=row,column=0)
            a = StringVar()
            self.NewEntries.append(a)
            self.NewTable = self.table
            
            # Fill it in
            if ( col == self.parent.whichCol.get() ):
                a.set( self.parent.entryText.get() )
                
            entry = Entry(f,bg="White",textvariable=a)
            entry.grid(row=row,column=1)
            row = row + 1
        f.pack()

    
    def apply(self):
        print "Creating new entry in table",self.NewTable
        entries = {}
        for colname,entry in zip(config.getEntryCols(self.NewTable),
                                 self.NewEntries):
            print "\t",colname,"\t",entry.get()
            entries[colname] = entry.get()

        db.addEntries((entries,),self.NewTable)
        return 1
    
#######################################



class FileListFrame(Frame):
    def __init__(self,parent,files):
        self.parent = parent
        self.files = files
        self.displayFrame = None
        self.tFrame = None
        Frame.__init__( self, parent, relief=RAISED, bd=1 )

    def setDisplayFrame(self,frame):
        self.displayFrame = frame
        
    def enableExplore(self,result=None):
        pass

    def showItem(self, result):
        if ( len(self.listbox.curselection()) == 0 ):
            return
        
        item = self.listbox.curselection()[0]
        value = self.listbox.get(item)
        if ( isinstance(value,tuple) ):
            value = list(value)[0]
            
        entryTag = {"filename":SimpleDBValue(value)}
        # Fill display frame with stats about this item
        entry = db.getEntries(entryTag,
                              config.getEntryCols(config.getTableName()),value)[0]
        row=0
        if ( self.tFrame is not None ):
            self.tFrame.pack_forget()
            self.tFrame.destroy()
            
        self.tFrame = Frame(self.displayFrame)

        # Get all of the attributes
        for col in config.getEntryCols(config.getTableName()):
            Label(self.tFrame, text=col).grid(row=row,column=0)
            Label(self.tFrame, text=entry[row]).grid(row=row,column=1)
            row = row + 1

        # And now, any linked attributes
        linkedItems = config.getLinks(db,entryTag)
        for label,links in linkedItems:
            print "LABEL:",label
            Label(self.tFrame, text=label).grid(row=row,column=0)
            if ( len(links) > 0 ):
                for link in links:
                    print "LINK:",link
                    Label(self.tFrame, text=link[1]).grid(row=row,column=1)
                    row = row + 1
            else:
                Label(self.tFrame, text="(none)").grid(row=row,column=1)
                row = row + 1
            
        self.tFrame.pack()
    
    def setResults(self,results,elapsedTime):
        pass

    def getCommonPrefix(self,s1,s2):
            prefix = []
            i = 0
            common_len = min(len(s1), len(s2))
            while i < common_len:
                if s1[i] != s2[i]:
                    break

                prefix.append(s1[i])
                i += 1
            prefix = ''.join(prefix)
            return prefix
        
    def setContents(self,entries,setWidth=True):
        self.commonString = entries[0]
        self.listbox.delete(0, END)
        for item in entries:
            self.commonString = self.getCommonPrefix(self.commonString, item)
            self.listbox.insert(END,item)

        # Resize
        maxX = 0
        for i in range(0,self.listbox.size()):
            a = self.listbox.get(i)
            maxX = max(maxX, len(a) )
        maxX = min(maxX, 100)
        

        if (setWidth):
            self.listbox.configure(width=maxX)
        
    # Hides all entries with the given column set
    def hideWithColumn(self,col):
        # If it's not in the main table, then it's multi-valued,
        # and we can have any number of them.
        if (config.getEntryCols().count(col) == 0):
            print "Ignoring multivalued item..."
            return

        entries = db.getEntries({col:MultiDBValue(["","Unknown"])},
                                ["filename"])
        self.setContents(entries,False)
        
    def getSelection(self):
        return [self.listbox.get(idx) for idx in self.listbox.curselection()]

    def getCommonString(self):
        return self.commonString
    
    def makeUI(self):
        self.label = Label(self, text="Files")
        self.label.pack(side=TOP)
        lb = Frame(self, relief=RAISED, bd=1)
        vscrollbar = Scrollbar(lb, orient=VERTICAL)
        hscrollbar = Scrollbar(lb, orient=HORIZONTAL)
        listbox = Listbox(lb,
                          selectmode=EXTENDED,
                          exportselection=0, # Don't lose selection if other is hilited
                          yscrollcommand=vscrollbar.set,
                          xscrollcommand=hscrollbar.set,
                          bg="White")
        vscrollbar.config(command=listbox.yview)
        vscrollbar.pack(side=RIGHT, fill=Y)
        hscrollbar.config(command=listbox.xview)
        hscrollbar.pack(side=BOTTOM, fill=BOTH)
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
        listbox.bind("<Double-Button-1>", self.showItem)
        listbox.bind("<Button-1>",self.enableExplore)
        self.listbox = listbox
        lb.pack(side=TOP,fill=BOTH,expand=1)

        self.setContents(self.files)

def optionsFromString(str, dataType,commonItems):
    output = []
    separators = ["_", "-", "@","/", "+","."]
    # Pull off the last ".", and everything after, as well
    # as the common prefix.
    if ( isinstance(str,tuple) ):
        str = list(str)[0]
    str = str[:str.rfind(".")]
    for common in commonItems:
        str = str.replace(common,"")

    for sep in separators:
        str = str.replace(sep," ")

    # Now, if the data type is "text", then collect
    # a list of words.
    items = []
    if ( dataType == "text" ):
        output = [str]
        items = [item.title() for item in str.split()]

        # Now also cull out any numbers
        for n in range(0,10):
            str = str.replace(repr(n)," ")
        numItems = [item.title() for item in str.split()]

        # Add any items in numItems that aren't yet in items
        for item in numItems:
            if ( items.count(item) == 0 ):
                items.append(item)
        # TODO - also query database for items LIKE item.
        
        output.extend(items)
        # Now add other items
        # 12,23,34,45,etc.
        # 123,234,345, etc.
        for numItemsToStick in range(2,len(items)+1):
            for index in range(0,len(items)-numItemsToStick+1):
                output.append( " ".join(items[index:index+numItemsToStick]))

    
    elif ( dataType == "INTEGER" ):
        # If it's an integer, then restrict the items
        # to just the integer portions (if any).
        items = [item for item in str.split() if isinstance(item,int)]
        output.extend(items)
    
        # We can also look for other integer patterns in the
        # main string
        numbers = re.findall( "[0-9]+", str )

        # Add them, making sure they really look like ints
        output.extend([repr(int(num)) for num in numbers])
    
    return output


def calculateOptions( selectedItems, column, common ):
    table = config.tableForColumn(column)
    dataType = config.getColumnType(column,table)
    
    if ( len(selectedItems) == 1 ):
        # OLD return optionsFromString(selectedItems[0], dataType, common)
        opts = optionsFromString(selectedItems[0], dataType, [common])
        # Get suggestions from the database
        dbSuggestions = config.getDBItems(column, db)

        # Now, combine these intelligently to create a better ordered list.
        retval = []
        for opt in opts:
            opttest = opt.lower().strip()
            # Change if statement to do better matching!
            retval.extend( [ dbitem for dbitem in dbSuggestions if dbitem.lower().strip() == opttest ] )
        retval.extend(opts)
        return retval
        
    else:
        # If we have multiple items, then collect suggestions from
        # each, and only show those that are common among all items
        # TODO: Maybe select those that are in a majority?
        suggestionList = []
        for item in selectedItems:
            suggestionList.append( optionsFromString(item, dataType, [common]) )

        # Grab the first list. Only add items from it that are also
        # present in the other lists.
        selectedItems = []
        baseList = suggestionList.pop()
        for item in baseList:
            okay = True
            for lists in suggestionList:
                if ( lists.count(item) == 0 ):
                    okay = False
                    break
            if (okay):
                selectedItems.append(item)
            
        return selectedItems

class DBFrame(Frame):
    def __init__(self,parent,columns,listframe):
        self.parent = parent
        self.columns = columns
        self.entryText = StringVar()
        self.optionText = StringVar()
        self.optionText.trace_variable("w",self.optionChanged)
        self.whichCol = StringVar()
        self.listframe=listframe
        Frame.__init__( self, parent )
        self.hideOkay = 0

    def optionChanged(self,a,b,c):
        print "Option changed to",self.optionText.get()
        print "Changing entry from",self.entryText.get()
        self.entryText.set( self.optionText.get() )
        
    def setColumn(self):
        # Ideally, we'd like to get the stuff out of here
        # without the /scratch/.VTMP/... junk.
        # What to do?
        selected = self.listframe.getSelection()
        common = self.listframe.getCommonString()

        if ( len(selected) > 0 ):
            print "Something selected, going to add options:"
            options = calculateOptions( selected, self.whichCol.get(), common )
            m = self.opt.children['menu']
            m.delete(0,END)
            for val in options:
                m.add_command(label=val,command=lambda v=self.optionText,l=val:v.set(l))
            if ( len(options) > 0 ):
                self.optionText.set(options[0])
        else:
            print "Nothing yet selected, waiting..."

        print "Set Column = which col is",self.whichCol.get()
        if ( self.hideOkay ):
            self.listframe.hideWithColumn(self.whichCol.get())

    def clearCol(self):
        self.whichCol.set("")
        self.entryText.set("")
        
    def doSet(self,dummy=None):
        col = self.whichCol.get()
        print "Set",self.entryText.get(), "into column",col
        print self.listframe.getSelection()
        entries = []
        print "SELECTION IS",len(self.listframe.getSelection())
        for item in self.listframe.getSelection():
            d = {"filename" : item,
                 col:self.entryText.get()}
            entries.append(d)

        table = config.tableForColumn(col)
        
        # If the table is the primary table for the config, then
        # just update the database.
        if ( config.isPrimaryTable(table) ):
            db.updateEntries(table, "filename", entries)
            
        # Otherwise, create a popup to fill out all the remaining
        # entries before adding to the db.
        else:
            # If an entry for this data already exists in the database,
            # then just add a link
            tag = {col:SimpleDBValue(self.entryText.get())}
            print "TAG IS",self.entryText.get(),table,col
            res = db.getEntries( tag, table=table )
            

            result = 1
            if ( len(res) == 0 ):
                # Pop up a new window
                result = EntryDialog(self,table,"Add Entry")

            # Now add the links
            print "ADDING LINKS FOR ENTRIES",entries
            config.addLinks( db, entries, tag ) 

        # And finish
        db.commit()
        
    def makeUI(self):
        # Frame 
        nfFrame = Frame(self,relief=GROOVE,bd=1)

        # Columns
        colFrame = Frame(nfFrame)
        Button( colFrame,
                text="Clear",
                command=self.clearCol
                ).pack(side=LEFT)
        for col in self.columns:
            b = Radiobutton(colFrame,
                            text=col,
                            value=col,
                            variable=self.whichCol,
                            indicatoron=1,
                            command=self.setColumn)
            b.pack(side=LEFT)
        colFrame.pack(side=TOP)

        setFrame = Frame(nfFrame)

        eFrame = Frame(setFrame)
        entry = Entry(eFrame, textvariable=self.entryText,bg="White")
        entry.bind("<Return>",self.doSet)
        entry.pack(side=TOP)
        self.opt = OptionMenu(eFrame,self.optionText,[])
        self.opt.pack(side=BOTTOM)
        eFrame.pack(side=LEFT)
            
        setButton = Button( setFrame,
                            text="Set",
                            command=self.doSet )
        setButton.pack(side=RIGHT)
        setFrame.pack(side=TOP)

        Separator(nfFrame).pack(fill=X,expand=1,pady=5,side=BOTTOM)
        displayFrame = Frame(nfFrame)
        self.listframe.setDisplayFrame(displayFrame)
        displayFrame.pack(side=BOTTOM)
        nfFrame.pack( side=TOP,fill=X,expand=1,pady=5 )


        
        
    
# Get the database name
def usage(prog):
    print "Usage: %s dbfile" % progname
    sys.exit(1)

import sys
from Config import *
from DBInterface import *
progname = sys.argv[0]
if ( len(sys.argv) < 2 ):
    usage(progname)
    
dbname = sys.argv[1]
config = ConfigFactory.GetConfigByTable( GetDBTable( dbname ) )
db = DBInterface(config,dbname)
cols = config.getSettableCols()
files = [entr[0] for entr in db.getEntries({},["filename"])]

root = Tk()
root.protocol("WM_DELETE_WINDOW", cleanup)
root.title("Set Database Tags (v0.1)")

# create Menu
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=cleanup)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

# Create list of files
#print "files",files
fileListFrame = FileListFrame(root,files)
fileListFrame.makeUI()
fileListFrame.pack(side=LEFT,fill=BOTH,expand=1)


# Create the DB Frame
dbFrame = DBFrame(root, cols,fileListFrame)
dbFrame.makeUI()
dbFrame.pack(side=RIGHT,fill=Y)


# Enter main loop
root.mainloop()

