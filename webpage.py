#!/usr/bin/python

# Main page:
# Form for DB file
# Form entry for num items per page

# DB Page: Inputs are dbname and pagenum
# Links for each table (anchor, same page)
# Table for each table (main,aux) in the db

# To show main entry links:
#  - Have the first 2 shown, plus a link to see all?
#  


import cgitb; cgitb.enable()
import cgi

print "Content-Type: text/html; charset=utf-8\n\n"
print "<html>"
print "<head><style type=\"text/css\">\
table.sample {\
	border-width: 1px 1px 1px 1px;\
	border-spacing: 2px 2px;\
	border-style: outset outset outset outset;\
	border-color: black black black black;\
	border-collapse: separate;\
	background-color: white;\
}\
table.sample th {\
	border-width: 1px 1px 1px 1px;\
	padding: 1px 1px 1px 1px;\
	border-style: outset outset outset outset;\
	border-color: ;\
	background-color: rgb(250, 240, 230);\
	-moz-border-radius: 3px 3px 3px 3px;\
}\
table.sample td {\
	border-width: 1px 1px 1px 1px;\
	padding: 1px 1px 1px 1px;\
	border-style: outset outset outset outset;\
	border-color: ;\
	background-color: rgb(250, 240, 230);\
	-moz-border-radius: 3px 3px 3px 3px;\
}\
</style></head>"

print "<body>"

import sys
sys.path.append("/usr/local/apps/MusicDir")

from DBInterface import *
from Config import *

# Need to get via form or param!
dbname = "/usr/local/apps/MusicDir/full.db"

config = ConfigFactory.GetConfigByTable( GetDBTable( dbname ) )
config.setDB( dbname )

db = DBInterface(config, dbname)
print "Database has",db.getNumEntries(),"entries"

entries = db.getEntries( {} )
numCols = len(config.tags)

print "<table class=sample>"
print "<tr>"
for tag in config.tags:
    print "<th>%s</th> " % (tag.title())
print "</tr>"

colors = ["white", "green"]
which = 0

ENTRYCAP = 500
for entry in entries[:ENTRYCAP]:
    print "<tr bgcolor=%s>" % (colors[which])
    for item in entry:
        print "<td style='font-size:10pt'>%s</td> " % (item.encode("latin-1"))
    print "</tr>"
    which = (which + 1) % 2
print "</table>"

print "</body></html>"

