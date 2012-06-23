from pysqlite2 import dbapi2 as sqlite
from Config import *
from DBValue import *

_DefaultDB = "/home/luke/Projects/MusicDir/full.db"

def GetDBTable(dbname):
  if (dbname is None):
    dbname = _DefaultDB
  con = sqlite.connect(dbname)
  cur = con.cursor()
  cur.execute("select name from sqlite_master where type='table'")
  all = cur.fetchall()
  tablename = ""
  for t in all:
    if ( t[0].endswith("Info") ):
      tablename = t[0]
      break
  con.close()
  return tablename

def GetAllTables(dbname):
  con = sqlite.connect(dbname)
  cur = con.cursor()
  cur.execute("select name from sqlite_master where type='table'")
  all = cur.fetchall()
  tables = []
  for t in all:
    if ( t[0] ):
      tables.append(t[0])
  con.close()
  return tables

class DBInterface:
  
  def __init__(self, config, dbname=_DefaultDB):
    self.con = sqlite.connect(dbname)
    self.tableName = config.getTableName()
    self.columns = config.getColumnsForTable(self.tableName)
    self.primary = config.getPrimaryColumnForTable(self.tableName)
    self.config = config

  def __del__(self):
      self.con.close()

  
  
  def clear(self):
      cur = self.con.cursor()
      # Drop all tables and recreate them
      for table in self.config.getTableNames():
        try:
          cur.execute("drop table %s" % table);
        except sqlite.OperationalError,e:
          print "Couldn't drop table:",e

        createString = "create table %s (" % table
        last = ","
        cols = self.config.getColumnsForTable(table)
        for tag in cols:
          if (tag == cols[len(cols)-1]):
              last = ");"
          createString += " %s %s%s" % (tag,self.config.getColumnType(tag,table),last)
        print "CREATE:",createString
        cur.execute(createString)
      

  def getNumEntries(self, table=None):
    if ( table is None ):
      table = self.tableName
    cur = self.con.cursor()
    cur.execute("select * from %s" % table)
    return len(cur.fetchall())
  
  def printStats(self,table=None):
    if ( table is None ):
      table = self.tableName
      
    # Print number of rows in tables?
    cur = self.con.cursor()
    cur.execute("select * from %s" % table)
    print len(cur.fetchall())

  # For each entry in entries, update each row with
  # the extra columns where the entry tag matches the match_tag.
  # I.e., to update cols foo and bar in a table, matching filename,
  # match_tag must be 'filename', and entries is a list of dicts
  # containing the keys 'filename', 'foo', and 'bar'
  def updateEntries(self,table, match_tag,entries):
      cur = self.con.cursor()
      for entry in entries:
        updateStr = "update %s set " % (table)
        values = []
        for col in entry.keys():
          if ( col != match_tag):
            updateStr += "%s = (?)," % (col)
            values.append(entry[col])

        # Take off the last ','
        updateStr = updateStr[0:updateStr.rfind(",")]

        # Add where clause to match tag
        if ( entry[match_tag].find("\'") == -1 ):
          updateStr += " where %s = '%s'" % (match_tag,entry[match_tag])
        elif ( entry[match_tag].find("\"") == -1 ):
          updateStr += " where %s = \"%s\"" % (match_tag,entry[match_tag])
        else:
          raise Exception("Don't know how to quote things like " + entry[match_tag])
          
        # print updateStr, "VALS:",values
        cur.execute(updateStr,values)

  # If there is no entry matching match_tag, then this functions
  # like addEntries(). Else, it functions like updateEntries().
  # Returns the number of entries added/updated
  def updateOrAddEntries(self, table, match_tag, entries):
    cur = self.con.cursor()

    entryCols = entries[0].keys()

    # See if the entry already exists.
    match_entries = self.getEntries( match_tag, columns=entryCols,unique=True,table=table )

    # No matches means we need to do an 'add'
    if ( len(match_entries) == 0 ):
      #print "\tAdd"
      self.addEntries(entries, table)
      return len(entries)
    else:
      # We matched, so just do an update.
      #print "\tUpdate"
      
      # Optimization - remove duplicates from entries that
      # are in match_entries
      #print match_entries
      final_entries = []

      for entry in entries:
        this_entry = {}
        for index,item in enumerate(entry.keys()):
          #print match_entries[0][index],"->",entry[item]
          if ( match_entries[0][index] != entry[item] ):
            this_entry[ item ] = entry[ item ]
        if ( len(this_entry.keys()) == 0 ):
          pass
          #print "\t\tUPDATE NOT NEEDED for entry",entry
        else:
          # Also need match key!
          this_entry[ match_tag.keys()[0] ] = str(match_tag.values()[0])
          final_entries.append(this_entry)

      if ( len(final_entries) == 0 ):
        pass #print "NO UPDATE!"
      else:
        self.updateEntries( table, match_tag.keys()[0], tuple( final_entries ) )

      return len(final_entries)
      
    
  def addEntries(self,entries,table=None):
      if (table is None):
        table = self.tableName
      cur = self.con.cursor()

      #values  = [val.values() for val in entries]
      values = []
      entryCols = self.config.getEntryCols(table)
      #print entryCols
      for val in entries:
          theList = []
          for key in entryCols:
            theList.append( unicode(str(val[key]),"latin-1") )
          values.append(theList)
      #print "VALUES ARE " , values
      
      
      # Add the given entries to the database
      # Entries will be a list of dictionaries with tags and values.
      # WAS insertStr = "insert into " + self.tableName + " " + str(tuple(self.columns)) + " values ("
      
      insertStr = "insert into " + table + " " + str(tuple(entryCols)) + " values ("
      for i in range(0,len(entryCols)-1):
          insertStr += "?, "
      insertStr += "?)"
      print "InsertStr = -%s-" % insertStr
      print values
      cur.executemany( insertStr, values )

  def dumpDB(self,table=None):
    if (table is None):
      table = self.tableName
      
    cur = self.con.cursor()
    cur.execute("select * from %s" % table)
    for line in cur.fetchall():
      print line
  
  def removeEntries(self,entries):
      # Delete given entries from the database
      # Entries are a list of entries in the primary column
      deleteStr = "delete from %s where %s = ?" % (self.tableName, self.primary)
      con.executemany(deleteStr,entries)
      
  def commit(self):
      self.con.commit()

  # Gets entries from the database:
  # Tags = Dict of items to match
  # Columns = which columns to select, None for all
  # Unique = force selection to be unique
  # Table = which table to select from
  def getEntriesOld(self,tags,columns=None,unique=False,table=None):
      if (table is None):
        table = self.tableName
      # Tags are a list of pairs [col,value] for the where clause.
      cur = self.con.cursor()
      if columns is None:
          colStr = "*"
      else:
          colStr = ""
          for item in columns:
              colStr += item + ", "
          colStr = colStr[0:colStr.rfind(",")]

      if ( unique ):
          selectStr = "select distinct "
      else:
          selectStr = "select "
      selectStr += "%s from %s " % ( colStr, table )

      if ( len(tags.keys()) > 0 ):
        selectStr += "where "
        vals = []
        for key in tags.keys():
          if ( not isinstance( tags[key], DBValue ) ):
            print "Tags",tags,"Fucked key",key,selectStr
            raise Exception("we're fucked, need a DBValue")
          dbstr,dbvals = tags[key].emitSQL(key)
          selectStr += dbstr + " and "
          vals.extend(dbvals)
          
        selectStr = selectStr[0:selectStr.rfind("and")-1]
        cur.execute(selectStr, tuple(vals))
      else:
        cur.execute(selectStr)
        
      return cur.fetchall()
    
  # Returns a list of all tables contained
  # in the list of tags and columns
  def _getTables(self,tags,columns):
    
    # Grab the list of tables for each item
    # Build a dictionary, so that we get easy
    # uniqueness testing.
    tableList = {}
    for item in tags:
      # DEBUG print "Tag item",item
      for table in item.getTableList():
	tableList[table] = 1

    for col in columns:
      # DEBUG print "Col item",col
      # DEBUG print "Col zero:",col[1]
      tableList[ col[1] ] = 1

    # Now, simply return the keys from the table List
    return tableList.keys()
    
    

  # Gets entries from the database:
  # Tags = List of DBValue items for matching.
  # Columns = which columns to select:
  # 	Format: A list of pairs - (column,table) OR
  #             a single table name. If in the second
  #             form, it will select all values from the table.
  # Unique = force selection to be unique
  def getEntries(self,tags,columns,unique=False):

      # DEBUG print "GET ENTRIES:"
      # DEBUG print "Tags:\t"
      # DEBUG for t in tags:
      # DEBUG   print "\t\t",str(t)
      # DEBUG print "Cols:\t",columns
      # First, start select statement
      if ( unique ):
          selectStr = "select distinct "
      else:
          selectStr = "select "

      # Grab a list of all the tables we need.
      tableList = self._getTables(tags,columns)
      # DEBUG print "Table list is",tableList

      # Add the list of columns/tables to be selected
      # If 'columns' is a single string, then it will be
      # '* from <table>'
      # DEBUG print "COLUMNS IS",columns
      if ( isinstance( columns, type([]) ) ):
	# Grab all of the col.table items
	colStr = ""
      	for (col,table) in columns:
          colStr += "%s.%s, " % ( table,col )
        colStr = colStr[0:colStr.rfind(",")]
	selectStr += colStr + " "

	# Add the FROM clause
	fromStr = "from "
	for table in tableList:
	  fromStr += "%s, " % (table)

	selectStr += fromStr[0:fromStr.rfind(",")] + " "
      else:
	# This is just "* from <table>"
	selectStr += " * from %s " % (columns)
   
      # Now create the WHERE clause (if needed),
      # and execute the statement
      cur = self.con.cursor()
      if ( len(tags) > 0 ):
	selectStr += "where "
        vals = []
        for tag in tags:
          if ( not isinstance( tag, DBValue ) ):
	    print "Tags",tags,"has a bad tag",tag,selectStr
            raise Exception("we're hosed, need a DBValue")
          dbstr,dbvals = tag.emitSQL()
          selectStr += dbstr + " and "
          vals.extend(dbvals)
          
        selectStr = selectStr[0:selectStr.rfind("and")-1]
        # DEBUG print "New Get Entries Select Str:"
        # DEBUG print "\t-%s-" % (selectStr)
        # DEBUG print "\tValues:",vals
        cur.execute(selectStr, tuple(vals))
      else:
        # DEBUG print "New Get Entries Select Str (1):"
        # DEBUG print "\t-%s-" % (selectStr)
        cur.execute(selectStr)
        
      return cur.fetchall()
