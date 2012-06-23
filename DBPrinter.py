#!/bin/env python

from Config import *
from DBInterface import *

db = DBInterface("cds.db", AudioConfig )

print db.getEntries( {}, ["genre"], True )

