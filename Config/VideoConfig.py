from ConfigBase import Config
from TreeNodes import *
from Formats import *
from DBInterface import DBInterface
from Aggregators import *
from Table import *

class VideoConfig(Config):

    VideoTags = ("filename","title","rating","virtual")
    VideoPrimary = "ID"
    VideoFormat = "format"
    

    def __init__(self):
        columns = [Column("filename",readonly=1),
                   Column("title"),
                   Column("rating",Column.Int),
                   Column("virtual",Column.Boolean),
                   Column("ID",Column.Primary,readonly=1),
                   Column("format",readonly=1)]
        
        self.mainTable = MainTable(format="format",
                                   name="VideoInfo",
                                   columns=columns,
                                   primary="ID")

        columns = [Column("ID", Column.Primary,readonly=1),
                   Column("name"),
                   Column("hair"),
                   Column("celeb",Column.Boolean),
                   Column("type")]
        self.starTable = AuxiliaryTable(name="Stars",
                                        columns=columns,
                                        primary="ID",
                                        major="name")

        self.starLinkTable = LinkTable( name="StarVideo",
                                        auxTable=self.starTable,
                                        mainTable=self.mainTable)
        self.starTable.setLinkedTable(self.starLinkTable)
        
        self.tables = [self.mainTable,
                       self.starTable,
                       self.starLinkTable]
        
        Config.__init__(self)

        
    def makeTree(self):
        db = DBInterface(self, self.dbname)

        #############################################################
        titleDefault = FileNode("VideoInfo", "title", db, TitleFormatConverter("VideoInfo") )
        titleSpecials = None
        titleTree = DBNode( "title",
                            "VideoInfo", 
                            "title",
                            db,
                            TitleFormatConverter("VideoInfo"),
                            titleDefault,
                            titleSpecials )
        basedict = {}
        basedict["ByTitle"] = titleTree
        #############################################################

        #############################################################
        ratingDefault = titleTree
        ratingSpecials = None
        ratingTree = DBNode("rating",
                            "VideoInfo", 
                            "rating",
                            db,
                            SimpleFormatConverter("VideoInfo", "rating"),
                            ratingDefault,
                            ratingSpecials )
        basedict["ByRating"] = ratingTree
        #############################################################

        #############################################################
        virtualDefault = titleTree
        virtualSpecials = None
        virtualTree = DBNode("virtual",
                             "VideoInfo", 
                             "virtual",
                             db,
                             SimpleFormatConverter("VideoInfo", "virtual"),
                             virtualDefault,
                             virtualSpecials )
        basedict["Virtual"] = virtualTree
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


_tmp = VideoConfig()

