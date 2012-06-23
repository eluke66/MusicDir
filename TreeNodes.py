import os, errno
from DBValue import *

debug = False

class Node:
    ReadDir = 0
    GetAttr = 1
    LookupFile = 2

    # Returns an lstat entry for the given path and type.
    # Type is one of ReadDir, GetAttr, or LookupFile. Each node
    # should implement GetAttr, and one of ReadDir or LookupFile.
    # currentSelectList is a list of DBValues,
    # which is used to select items from the database.
    def process(self,path,type,currentSelectList):
        pass

    # Returns the next node in the tree for the given path. Can
    # raise an exception if the node is intended to be a leaf node.
    # Non-leaf nodes will modify currentSelectList 
    def getTree(self,path,type,currentSelectList):
        pass
    
class BaseNode(Node):
    def __init__(self,basedict):
        self.basedict = basedict

    def process(self,path,type,currentSelectList):
        # Path should be one of the items in basedirs
        if ( type == Node.ReadDir ):
            if (debug): print "ReadDir"
            return self.basedict.keys()
        elif ( type == Node.GetAttr ):
            if (debug): print "LSTAT ."
            return os.lstat(".")
        elif ( type == Node.LookupFile ):
            raise Exception("Can't look up file on synthetic directory!")
        else:
            print "Unknown process type " + str(type)
    
    def getTree(self,path,type,currentSelectList):
        if (debug): print "BASE GETTREE: Path is -%s-"%path
        t,r = getPathTop(path)
        return self.basedict[t.rstrip("/")]

class DBNode(Node):
    def __init__(self, name, table, tag, db, converter, defaultNode, specialNodes=None):
        self.name = name
        self.table = table
        self.tag  = tag
        self.converter = converter
        self.defaultNode = defaultNode
        self.specialNodes = specialNodes
        self.db = db
        
    def process(self,path,type,currentSelectList):
        if (debug): print "DBProcessing",self.name
        if ( type == Node.ReadDir ):
            if (debug):
                print "Current select list:"
                for item in currentSelectList:
                    print "\t-%s-" % (str(item))
            if (debug): print "Tag is",self.tag,
            if (debug): print "default subnode tag is",self.defaultNode.tag
            
            converter = self.converter
            entries = self.db.getEntries( currentSelectList, converter.getTags(), True)
            entrydicts = [dict(zip(converter.getTags(),entry)) for entry in entries]
            entries = [converter.formatToName(entry) for entry in entrydicts]
            entries.sort()
            if (debug): print "\n%%%%%\nWe have",len(entries),"entries"
            return entries
        elif ( type == Node.GetAttr ):
            return os.lstat(".")
        elif ( type == Node.LookupFile ):
            raise Exception("Can't look up file on synthetic directory!")
        else:
            print "DB Unknown process type " + str(type)

    def getTree(self,path,type,currentSelectList):
        if (debug): print "DBGetTree",self.name,path
        t,r = getPathTop(path)

        returnNode = self.defaultNode
        if (debug): print currentSelectList
        if self.specialNodes is not None:
            if (self.specialNodes.has_key(t.rstrip("/"))):
                if (debug): print "Using special node",t.rstrip("/")
                returnNode = self.specialNodes[t.rstrip("/")]

        if ( not isinstance( returnNode, FileNode ) ):
            if (debug): print "Adding",str(SimpleDBValue(t.rstrip("/"),self.table,self.tag))
            currentSelectList.append(SimpleDBValue(t.rstrip("/"),self.table,self.tag))
            
        return returnNode


# Like a DBNode, but this node aggregates/filters items instead of doing just a simple
# switch.
class DBAggregateNode(DBNode):
    def __init__(self, name, table, tag, db, aggregator, converter, defaultNode, specialNodes=None):
        DBNode.__init__(self,name,table,tag,db,converter,defaultNode,specialNodes)
        self.aggregator = aggregator
        if (defaultNode is None):
            raise Exception("No default node for aggregate " + name)
        
    def process(self,path,type,currentSelectList):
        if (debug): print "DBAggregateProcessing",self.name
        if ( type == Node.ReadDir ):
            if (debug): print "Current select list:",currentSelectList
            if (debug): print "Tag is",self.tag,
            if (debug): print "default subnode tag is",self.defaultNode.tag
            
            converter = self.converter
            entries = self.db.getEntries( currentSelectList, converter.getTags(), True)
            entrydicts = [dict(zip(converter.getTags(),entry)) for entry in entries]
            entries = [converter.formatToName(entry) for entry in entrydicts]
            entries.sort()
            entries = self.aggregator.aggregate(entries)
            return entries
        elif ( type == Node.GetAttr ):
            return os.lstat(".")
        elif ( type == Node.LookupFile ):
            raise Exception("Can't look up file on synthetic directory!")
        else:
            print "DB Unknown process type " + str(type)

    def getTree(self,path,type,currentSelectList):
        if (debug): print "DBAggregateGetTree",self.name,path
        t,r = getPathTop(path)
        returnNode = self.defaultNode
        if self.specialNodes is not None:
            if (self.specialNodes.has_key(t.rstrip("/"))):
                if (debug): print "Using special node",t.rstrip("/")
                returnNode = self.specialNodes[t.rstrip("/")]

        if ( not isinstance( returnNode, FileNode ) ):
            if (debug): print "Adding",str(self.converter.getDBValue(t)),"for",t
            currentSelectList.append(self.converter.getDBValue(t))
        if (debug): print currentSelectList

        return returnNode

class FileNode(Node):
    def __init__(self,table,tag,db,converter):
        self.table = table
        self.tag = tag
        self.converter = converter
        self.db = db

    def lookupFile(self,path,currentSelect):
        global debug
        debug = True
        if (debug): print "Getting stats for file",path
        if (debug): print "Current select is",currentSelect

        # Use the converter to convert the path name to the appropriate real file
        entry = self.converter.nameToFormat(self.db, path, currentSelect)
        if (debug): print entry
        debug = False
        return entry
        
    def process(self,path,type,currentSelect):
        global debug
        if ( type == Node.GetAttr ):
            entry = self.lookupFile(path,currentSelect)
            if ( entry is None ):
                return -errno.ENOENT
            return os.lstat(entry)
        elif ( type == Node.LookupFile ):
            return self.lookupFile(path,currentSelect)
        elif ( type == Node.ReadDir ):
            raise Exception("Calling readdir on file %s" %path)
        else:
            print "File Unknown process type " + str(type)
                            
    def getTree(self,path,type,currentSelectList):
        raise Exception("File %s has no subtree for path %s" % (self.name,path))
        return None
    
def getPathTop(path):
    # Return everything up to and including the first "/"
    # as top, and then the rest
    index = path.find("/")+1
    if ( index == 0 ):
        return path,""
    return path[0:index], path[index:]

def processTree(path, node, processType, currentSelectList):
    if (debug): print "============================="
    if (debug): print "PROCESS TREE: CURRENT SELECT IS"
    if (debug):
        for item in currentSelectList:
            print "\t-%s-" % (str(item))
    # Get the current path top
    (top,rest) = getPathTop(path.rstrip("/"))

    if (debug): print "Top,rest = -%s-,-%s-" % ( top,rest)
    # If this is a leaf node, process the leaf node
    if ( len(rest) == 0 ):
        if (debug): print "***PROCESS",top
        return node.process(top,processType,currentSelectList)

    # Otherwise, process the node's subtree
    subtree = node.getTree( rest, processType, currentSelectList )
    return processTree( rest, subtree, processType, currentSelectList )
