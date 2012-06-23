#!/bin/env python
# encoding: latin-1

# Usage:
# dbloader.py dbfile style <path1> <path2> ....
import os.path
import sys

NameList = {}
DictList = {}


def processPath(path):
    set = ()
    subject = None
    tags = ()

    nameParts = splitPath(path)
    #DEBUGprint nameParts
    (names,maybenames,tags) = partsToItems(nameParts) 
    names = [item.title() for item in names]
    #DEBUGprint "NAMES:",names
    #DEBUGprint "Maybe:",maybenames
    #DEBUGprint "TAGS:",tags
    
    subject = findNameInDatabase(names,maybenames)
    return (set,subject,tags)

def findNameInDatabase(names, maybenames):
    dblist = loadDB()
    subDict = {}
    for n in findNames(names, dblist):
        subDict[n] = None
    #DEBUGprint subDict.keys()
    if ( len(subDict.keys()) == 0 ):
        print "Need to CREATE",names
    elif ( len(subDict.keys()) == 1 ):
        print "USING ", subDict.keys()[0]
    else:
        print "ASK Which:",subDict.keys()

def loadDB():
    return {"Kathy" : "stuff", "Kathy Lee" : "leestuff"}
        
def all_perms(str):
    if len(str) <=1:
        yield str
    else:
        for perm in all_perms(str[1:]):
            for i in range(len(perm)+1):
                yield perm[:i] + str[0:1] + perm[i:]


def findNames(names,dblist):
    # Create a list of all permutations of whitespace separated string of 
    # everything in the list
    subjects = []
    return doFindNames(names,dblist)
    
    
def listExcept(list, index):
    theList = []
    for i in range(0,len(list)):
        if ( i != index ):
            theList.append(list[i])
    return theList
    
def doFindNames(names,dblist):
    subjects = []
    for perm in all_perms(names):
        nameString = " ".join(perm)
        if ( dblist.has_key(nameString) ):
            subjects.append(nameString)
    for i in range(0,len(names)):
        subjects.extend( doFindNames( listExcept(names,i), dblist ) )
    return subjects
    
def findSubWords(string,list,testFn):
    while (len(string) > 0):
        for i in range(1,len(string)):
            testItem = string[0:i]
            if ( testFn(testItem) ):
                list.append(testItem)
        string = string[1:]
                
def partsToItems(nameParts):
    names = []
    maybenames = []
    tags = []
    
    for item in nameParts:
        for n in range(0,10):
            item = item.replace(repr(n)," ")
        if (inNameList(item)):
            names.append(item)
        elif inDictionary(item):
            tags.append(item)
            maybenames.append(item)
        else:
            # Split it into all possible combinations, and see if any of these are in the name list
            findSubWords(item, names, inNameList)
            findSubWords(item, tags, inDictionary)
            findSubWords(item, maybenames, inDictionary)
    
    return (names,maybenames,tags)
    
def splitPath(path):
    output = []
    separators = ["_", "-", "@","/", "+","."]
    commonItems = ["home", "met"]
    # Pull off the last ".", and everything after, as well
    # as the common prefix.
    str = path
    
    str = str[:str.rfind(".")]
    for common in commonItems:
        str = str.replace(common,"")

    for sep in separators:
        str = str.replace(sep," ")
        
    return str.split();
    
def inNameList(item):
    global NameList
    return NameList.has_key(item.upper())

def inDictionary(item):
    global DictList
    if ( len(item) < 3 ):
        return False
    return DictList.has_key(item.upper())
        
def loadNameList():
    global NameList
    nameHandle = file("Names", "r")
    for item in nameHandle.readlines():
        NameList[item.strip()] = None
    nameHandle.close()
    
def loadDictionary():
    global DictList
    dictHandle = file("/usr/share/dict/words", "r")
    for item in dictHandle.readlines():
        DictList[item.strip()] = None
    dictHandle.close()
    
loadNameList()
loadDictionary()    

for path in sys.argv[1:]:
    print "Processing",path
    (set, subject, tags) = processPath(path)
