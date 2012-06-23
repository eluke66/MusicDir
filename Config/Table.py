

class Column:
    Text    = "text"
    Int     = "INTEGER"
    Primary = "INTEGER PRIMARY KEY AUTOINCREMENT"
    Boolean = "INTEGER"
    
    def __init__(self,name,type=Text,readonly=0):
        self.name = name
        self.type = type
        self.readonly = readonly



class Table:

    def __init__(self, name, columns, primary):
        self.name = name
        self.columns = columns
        self.primary = primary

    def getName(self):
        return self.name

    def getColumns(self):
        return self.columns

    def getColumnNames(self):
        return [col.name for col in self.columns]

    def getSettableColumns(self):
        return [col.name for col in self.columns if col.readonly == 0]

    def getColumnType(self,column):
        col = self._column(column)
        return col.type

    def getPrimary(self):
        return self.primary

    def _column(self,name):
        for col in self.columns:
            if (col.name == name):
                return col
        return None

class AuxiliaryTable(Table):

    def __init__(self,name,columns,primary,major):
        self.link = None
        self.major = major
        Table.__init__(self,name,columns,primary)


    # Returns the major column - not the primary, but the
    # most important editable column (name, etc.)
    def getMajorCol(self):
        return self.major
        
    def setLinkedTable(self,link):
        self.link = link
        
    def getLinkedTable(self):
        return self.link

class LinkTable(Table):

    def __init__(self,name,auxTable,mainTable):
        self.auxCol = self._makeCol(auxTable)
        self.mainCol = self._makeCol(mainTable)
        self.auxTable = auxTable
        self.mainTable = mainTable
        
        columns = [ Column("ID",Column.Primary,readonly=1),
                    self.auxCol,
                    self.mainCol ]
        Table.__init__(self,name,columns,"ID")

    def _makeCol(self,table):
        colType = table.getColumnType(table.getPrimary())

        # Use int instead of Primary
        if (colType == Column.Primary):
            colType = Column.Int
            
        return Column(table.getName() + table.getPrimary(),
                      colType,
                      readonly=1)
        
    def getAuxTable(self):
        return self.auxTable
    

class MainTable(Table):

    def __init__(self,format,name,columns,primary):
        self.format = format
        Table.__init__(self,name,columns,primary)

    def getFormatColumn(self):
        return self.format
    
