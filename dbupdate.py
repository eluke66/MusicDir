#!/bin/env python
# encoding: latin-1

# Usage:
# dbupdate.py dbfile <path1> <path2> ....
import sys
import os.path
from Config import *
from DBInterface import *
from TagLoader import *

DEBUGLIST = []
LAST_PROCESS = "unset"
filesProcessed = 0
entriesUpdated = 0

def usage(progname):
    print "Usage: %s dbfile <path1> <path2> ..." % progname
    sys.exit(0)

def doProcessPath(arg, dirname, fnames):
    global DEBUGLIST
    
    #print arg,"DoProcessPath:",fnames
    for name in fnames:
        pathToProcess = dirname + "/" + name
        #print arg,"--> Processing",pathToProcess
        if ( DEBUGLIST.count( pathToProcess ) > 0 ):
            continue
            #raise Exception("Already processed "+pathToProcess+" last was " + LAST_PROCESS)
        DEBUGLIST.append(pathToProcess)
        processPath(pathToProcess, arg)
        #fnames.remove(name)
        
def processPath(path, indent):
    global LAST_PROCESS
    # If a directory, process it recursively
    if ( os.path.isdir(path) ):
        #print indent,"Walking",path
        LAST_PROCESS = path
        os.path.walk( path, doProcessPath, indent+" " )

    # If a file, process the file
    elif (os.path.isfile(path)):
        #print "PROCFILE",path
        processFile( os.path.normpath(path) )
    else:
        print "WTF kind of thing is -%s-" % path

def processFile(path):
    global db, filesProcessed, entriesUpdated
    # Process the file
    #print "Processing file -%s-" % path
    loader = TagLoaderFactory.GetLoader(path)
    if ( loader is not None ):
        filesProcessed += 1
        #print "\tWith loader",loader
        tags = loader.getTags(path)
        if ( tags is not None ):
            #print "Update/Add Entry for",tags["filename"]
            match = {"filename":SimpleDBValue(tags["filename"])}
            entriesUpdated += db.updateOrAddEntries( table=config.mainTable.getName(),
                                                     match_tag=match,
                                                     entries=(tags,) )
    
sys.argv.reverse()
progname = sys.argv.pop()
if ( len(sys.argv) < 1 ):
    usage(progname)
dbfile = sys.argv.pop()
if ( len(sys.argv) < 1 ):
    usage(progname)

paths = sys.argv



from AudioTagLoaders import *
from VideoTagLoaders import *
config = ConfigFactory.GetConfigByTable( GetDBTable( dbfile ) )
db = DBInterface(config,dbfile)

for path in paths:
    processPath( path, "" )
db.commit()

if (filesProcessed == 0):
    percent = 0.0
else:
    percent = float(entriesUpdated*100) / float(filesProcessed)
args = ( entriesUpdated, filesProcessed, percent)
print "Successfully updated %d / %d available files (%f%%)" % args


    
