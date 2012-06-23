#!/bin/env python

from Config import *
from DBInterface import *
import sys

def usage(prog):
    print "Usage: %s dbfile" % progname
    sys.exit(1)


progname = sys.argv.pop(0)
if ( len(sys.argv) < 1 ):
    usage(progname)
    
dbname = sys.argv.pop()
config = ConfigFactory.GetConfigByTable( GetDBTable( dbname ) )
db = DBInterface(config,dbname)

for table in config.getTableNames():
    print "TABLE %s has %d entries:" % ( table, db.getNumEntries(table) )
    db.dumpDB(table)

