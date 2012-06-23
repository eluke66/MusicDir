from ConfigBase import Config
from TreeNodes import *
from Formats import *
from DBInterface import DBInterface
from Aggregators import *
from Table import *

# Table configuration

### MAIN ###
# filename
# photoset (to group like items)
# ID
# format

### Subject ###
# ID
# name
# haircolor
# race

### Tags ###
# ID
# Description (legs, wet, etc.)


# Directory hierarchy:
# Name
#  All
#  <set...>
# Hair
#  Name
# Race
#  Name
# Tag
#  <tag...>
#   Name


class PictureConfig(Config):

    PictureTags = ("filename","photoset")
    PicturePrimary = "ID"
    PictureFormat = "format"
    

    def __init__(self):
        ##########  MAIN #############################
        columns = [Column("filename",readonly=1),
                   Column("photoset"),
                   Column("ID",Column.Primary,readonly=1),
                   Column("format",readonly=1)]
        
        self.mainTable = MainTable(format="format",
                                   name="PictureInfo",
                                   columns=columns,
                                   primary="ID")

        ##########  SUBJECT #############################
        columns = [Column("ID", Column.Primary,readonly=1),
                   Column("name"),
                   Column("hair"),
                   Column("race")]
        self.subjectTable = AuxiliaryTable(name="Subject",
                                           columns=columns,
                                           primary="ID",
                                           major="name")

        self.subjectLinkTable = LinkTable( name="SubjectPicture",
                                           auxTable=self.subjectTable,
                                           mainTable=self.mainTable)
        self.subjectTable.setLinkedTable(self.subjectLinkTable)

        ##########  TAGS #############################
        columns = [Column("ID", Column.Primary,readonly=1),
                   Column("description")]

        self.tagTable = AuxiliaryTable(name="Tag",
                                       columns=columns,
                                       primary="ID",
                                       major="description")

        self.tagLinkTable = LinkTable( name="TagPicture",
                                       auxTable=self.tagTable,
                                       mainTable=self.mainTable)
        self.tagTable.setLinkedTable(self.tagLinkTable)
        ################################################

        
        self.tables = [self.mainTable,
                       self.subjectTable,
                       self.subjectLinkTable,
                       self.tagTable,
                       self.tagLinkTable]
        
        Config.__init__(self)

        
    def makeTree(self):
        db = DBInterface(self, self.dbname)
        basedict = {}
        
        #############################################################
        idDefault = FileNode("PictureInfo", "ID", db, IDFormatConverter("PictureInfo") )
        idSpecials = None
        idTree = DBNode( "ID",
                         "PictureInfo",
                         "ID",
                         db,
                         IDFormatConverter("PictureInfo"),
                         idDefault,
                         idSpecials )
        basedict["ByID"] = idTree
        #############################################################

        #############################################################
        #setDefault = idTree
        #setSpecials = None
        #setTree = DBAggregateNode("rating",
        #                          "rating",
        #                          db,
        #                          SimpleFormatConverter("rating"),
        #                          ratingDefault,
        #                          ratingSpecials )
        #basedict["ByRating"] = ratingTree
        ##############################################################

        #############################################################
        #virtualDefault = titleTree
        #virtualSpecials = None
        #virtualTree = DBNode("virtual",
        #                     "virtual",
        #                     db,
        #                     SimpleFormatConverter("virtual"),
        #                     virtualDefault,
        #                     virtualSpecials )
        #basedict["Virtual"] = virtualTree
        #############################################################
        
        ########### NOT DONE ##############
        #basedict["ByStar"] = starTree
        #
        ###################################

        self.tree = BaseNode( basedict )
            
    def getTree(self):
        if ( self.tree is None ):
            self.makeTree()
        return self.tree


_tmp = PictureConfig()

