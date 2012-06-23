#!/bin/env python

from TagLoader import *

########################## MP3 ########

l = TagLoaderFactory.GetLoader("gump")
print l
l = TagLoaderFactory.GetLoader("gump.foo")
print l
l = TagLoaderFactory.GetLoader("gump.mp3")
print l
print l.getTags("gump.mp3")
l = TagLoaderFactory.GetLoader("Zorro.mp3")
print l
print l.getTags("Zorro.mp3")
l = TagLoaderFactory.GetLoader("mask.MP3")
print l
print l.getTags("mask.MP3")

########################## FLAC ########

l = TagLoaderFactory.GetLoader("zztop.flac")
print l
print l.getTags("zztop.flac")
