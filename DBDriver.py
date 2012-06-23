#!/bin/env python

from Config import *
from DBInterface import *

config = Config("InfoTable", Config.Audio )

db = DBInterface(":memory:", config)
db.clear()
db.printStats()


###
from TagLoader import *
l = TagLoaderFactory.GetLoader("zztop.flac")
entry = l.getTags("zztop.flac")
db.addEntries( (entry,) )
###
db.printStats()
db.dumpDB()


print db.getEntries( {} )
fname = {}
fname["filename"] = "zztop.flac"
print db.getEntries(fname)
print db.getEntries(fname, ["album"])

fname["filename"] = "fump.mp3"
print db.getEntries(fname)

