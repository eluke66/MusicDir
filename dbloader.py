#!/bin/env python
# encoding: latin-1

# Usage:
# dbloader.py dbfile style <path1> <path2> ....
import sys
import os.path
from Config import *
from DBInterface import *
from TagLoader import *



DEBUGLIST = []
LAST_PROCESS = "unset"
filesProcessed = 0

def usage(progname):
    print "Usage: %s dbfile style <path1> <path2> ..." % progname
    print "\tAvailable styles:","audio","video","picture"
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
    global db, filesProcessed
    # Process the file
    #print "Processing file -%s-" % path
    loader = TagLoaderFactory.GetLoader(path)
    if ( loader is not None ):
        filesProcessed += 1
        #print "\tWith loader",loader
        tags = loader.getTags(path)
        if ( tags is not None ):
            db.addEntries((tags,))
        #else:
        #    print "Not processing",path
    #else:
    #    print "No loader for",path
    
sys.argv.reverse()
progname = sys.argv.pop()
if ( len(sys.argv) < 2 ):
    usage(progname)
dbfile = sys.argv.pop()
if ( len(sys.argv) < 2 ):
    usage(progname)
style = sys.argv.pop()
if ( len(sys.argv) < 1 ):
    usage(progname) 
paths = sys.argv

if ( style == "audio" ):
    from AudioTagLoaders import *
    config = AudioConfig()
elif ( style == "video" ):
    from VideoTagLoaders import *
    config = VideoConfig()
elif ( style == "picture" ):
    from PictureTagLoaders import *
    config = PictureConfig()
else:
    print "Unknown style:",style
    usage(progname)
    
db = DBInterface(config,dbfile)
db.clear()

for path in paths:
    processPath( path, "" )
db.commit()

numFiles = db.getNumEntries()
if (filesProcessed == 0):
    percent = 0.0
else:
    percent = float(numFiles*100) / float(filesProcessed)
args = ( numFiles, filesProcessed, percent)
print "Successfully added %d / %d available files (%f%%)" % args


    

