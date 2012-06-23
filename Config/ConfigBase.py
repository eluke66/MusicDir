from fuse import Fuse
from DBInterface import *
from Formats import *
from Aggregators import *
from TreeNodes import *
debug = False


#
# DBInterface needs: tags, primary, tablename 
#
# Config currently holds:
#  tags, primary, tablename, tree
#
# Config references tree
# Tree references DB (DBNodes do, maybe can be given a DB?)
# Tree references config only to get DB...
#
# Thus, the heirarchy should be:
#  Config
#  |    \
#  Tree |
#      \|
#      DB
class Config:

    def __init__(self):
        self.tree = None
        self.dbname = None
        ConfigFactory.Register(self)

    def getColumnType(self,column,table):
        for tableItem in self.tables:
            if (table == tableItem.getName()):
                return tableItem.getColumnType(column)
        raise Exception("getColumnType - no such table %s" % (table))
        
    def getPrimaryColumnForTable(self,table):
        for tableItem in self.tables:
            if (table == tableItem.name):
                return tableItem.getPrimary()
            
        raise Exception("getPrimaryColumnForTable - no such table %s" % (table))
    
    def getColumnsForTable(self,table):
        for tableItem in self.tables:
            if (table == tableItem.name):
                return tableItem.getColumnNames()
            
        raise Exception("getColumnsForTable - no such table %s" % (table))

    def tableForColumn(self,column,returnName=True):
        whichTable = None
        for tableItem in self.tables:
            for col in tableItem.getColumnNames():
                if (col == column):
                    if ( whichTable is not None ):
                        raise Exception("Bad DB schema - multiple tables with column %s (%s,%s)" %
                                        (column,whichTable.getName(),tableItem.getName()))
                    whichTable = tableItem

        if ( whichTable is None ):
            raise Exception("No table has column %s" % (column))
        
        if ( returnName ):
            return whichTable.getName()
        
        return whichTable

    def isPrimaryTable(self,table):
        return table == self.mainTable.getName()

    def getDBItems(self,column,db):
        # Gets all items in the database in that column, unique-ified.
        table = self.tableForColumn(column)
        if ( self._linked(table) ):
            print "getDBItems() on linked tables isn't done yet!"
            return []
        else:
            items = [list(item)[0] for item in db.getEntries({},[column],True,table)]
            print "DB suggests",len(items),"items"
            return items

    # All settable columns for the main table, which
    # is all the settable columns for the main table,
    # plus all the links
    def getSettableCols(self):
        
        # Start with the main table's settable columns
        retval = self.mainTable.getSettableColumns()
        
        # For each auxiliary table
        for aux in self._getAuxTables():
            # Add the major column
            retval.append(aux.getMajorCol())
        
        return retval
    
    def _linked(self, table):
        from Table import AuxiliaryTable
        for tableItem in self.tables:
            if ( table == tableItem.getName() ):
                return isinstance(tableItem,AuxiliaryTable)

    def _getAuxTables(self):
        from Table import AuxiliaryTable
        retval = []
        for tableItem in self.tables:
            if ( isinstance(tableItem,AuxiliaryTable) ):
                retval.append(tableItem)
        return retval

    def getTableNames(self):
        return [t.getName() for t in self.tables]

    # Return a list of pairs:
    #  First item is "name" of link
    #  Second item is a list of link entries
    #   (Link entry is a list of all the matching items)
    def getLinks(self,db,entryTag):
        retval = []
        
        # Get the ID for the main table entry
        # matching entryTag
        mainID = db.getEntries(entryTag,
                               [self.mainTable.getPrimary()],
                               True,
                               self.mainTable.getName())
        
        # Now create a selector that will match the ID for this main
        # table entry in all of the link tables.
        colName = self.mainTable.getName()+self.mainTable.getPrimary()
        mainLinkTag = {colName:SimpleDBValue(mainID[0][0])}
        
        # Get all of the auxiliary tables
        auxTables = self._getAuxTables()
        
        # For each auxiliary table:
        for aux in auxTables:

            # Get the "link" name
            name = aux.getName()

            # Find all aux IDs in the link table
            # that match the main ID
            linkTable = aux.getLinkedTable()
            linkItems = db.getEntries( mainLinkTag,
                                       [aux.getPrimary()],
                                       True,
                                       linkTable.getName() )
            auxItems = []
            
            # Now, grab the aux items for each aux ID
            if ( len(linkItems) > 0 ):
                matches = [item[0] for item in linkItems]
                auxTag = {aux.getPrimary() :
                          MultiDBValue(matches)}
                auxItems = db.getEntries(auxTag,None,True,aux.getName())

            # And add the link name and results to the return values.
            retval.append( (name, auxItems) )
            
        return retval

    # For each entry in entries, create a link
    # between the tag and the entry in the appropriate
    # link table.
    def addLinks(self,db,entries,tag):
        print "TAG IS",tag
        # Find the auxiliary table containing the tag
        auxTable = self.tableForColumn(tag.keys()[0],False)
        print "AUX TABLE FOR",tag,"is",auxTable.getName()

        # Find the primary for the tag in the aux table
        auxPrimary = db.getEntries( tag,
                                    [auxTable.getPrimary()],
                                    True,
                                    auxTable.getName())
        auxID = auxPrimary[0][0]
        linkTable = auxTable.getLinkedTable()
        
        # For each entry:
        for entry in entries:
            # Find the primary for the entry in the DB.

            # Scoop out the tag...
            del entry[tag.keys()[0]]
            entryCol = entry.keys()[0]
            entryTag = { entryCol : SimpleDBValue(entry[entryCol]) }
            mainPrimary = db.getEntries( entryTag,
                                         [self.mainTable.getPrimary()],
                                         True,
                                         self.mainTable.getName() )
            mainID = mainPrimary[0][0]

            # Now create a link in the link table for the aux table
            linkEntry = {linkTable.auxCol.name  : auxID,
                         linkTable.mainCol.name : mainID}
            db.addEntries( (linkEntry,), linkTable.getName() )

    def getEntryCols(self,table):
        from Table import Column
        theTable = None
        for tableItem in self.tables:
            if (table == tableItem.name):
                theTable = tableItem
                break
            
        if ( theTable is None ):
            raise Exception("getEntryCols - no such table %s" % (table))

        return [ c.name for c in theTable.getColumns() if ( not (c.name == theTable.getPrimary() and c.type == Column.Primary) )]
    
    def setDB(self,dbname):
        self.dbname = dbname
        
    def getTableName(self):
        return self.mainTable.getName()
    
    def getTree(self):
        if ( self.tree is None ):
            self.makeTree()
        return self.tree

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

class ConfigFactory:
    ConfigMap = {}
    
    def GetConfigByTable(tableName):
        if ( ConfigFactory.ConfigMap.has_key( tableName ) ):
            return ConfigFactory.ConfigMap[ tableName ]
        raise Exception( "No matching configs for table " + tableName)
    
    def Register( config ):
        ConfigFactory.ConfigMap[config.getTableName()] = config
    
    GetConfigByTable = Callable(GetConfigByTable)
    Register = Callable(Register)
