#!/bin/env python
# encoding: latin-1


def verifyEntry(input,golden):
    retval = True

    for index,item in enumerate(golden.keys()):
        if ( golden[item] != input[index] ):
            print "Mismatch for entry",item,". Is",input[index],"should be",golden[item]
            retval = False

    return retval

# Usage:
# dbloader.py dbfile style <path1> <path2> ....
import sys
import os.path
from Config import *
from DBInterface import *

dbfile = "dbupdatetest.db"

# Update test for dbupdate.
entry1 = {"filename":"/filename1",
          "title":"title1",
          "artist":"artist1",
          "album":"album1",
          "year":"year1",
          "genre":"genre1",
          "track":"track1",
          "format":"format1"}
entry15 = {"filename":"/filename1",
           "year":"year15",
           "track":"track15"}
entry15_full = {"filename":"/filename1",
          "title":"title1",
          "artist":"artist1",
          "album":"album1",
          "year":"year15",
          "genre":"genre1",
          "track":"track15",
          "format":"format1"}
entry1DB = {"filename":SimpleDBValue("/filename1")}

entry2 = {"filename":"/filename2",
          "title":"title2",
          "artist":"artist2",
          "album":"album2",
          "year":"year2",
          "genre":"genre2",
          "track":"track2",
          "format":"format2"}
entry2DB = {"filename":SimpleDBValue("/filename2")}

config = AudioConfig()
db = DBInterface(config,dbfile)
db.clear()



# Call addEntry for an entry
db.addEntries( (entry1,), config.mainTable.getName() )

# Call getentry, ensure entry matches entry1
res = db.getEntries( entry1DB,entry1.keys() )
if (verifyEntry (res[0], entry1 )):
    print "-------> Initial add okay."

# Call updateoraddEntries for the given entry
db.updateOrAddEntries(table=config.mainTable.getName(),
                      match_tag=entry1DB,
                      entries=(entry15,))

# Call getEntry, ensure entry is updated
res = db.getEntries( entry1DB, entry1.keys() )
if (verifyEntry (res[0], entry15_full )):
    print "-------> Update existing okay."
    
# Call updateoraddEntries for a new item
db.updateOrAddEntries(table=config.mainTable.getName(),
                      match_tag=entry2DB,
                      entries=(entry2,))

# call GetEntry, ensure new item is there.
res = db.getEntries( entry2DB, entry2.keys() )
if (verifyEntry (res[0], entry2 )):
    print "-------> Update new okay."
