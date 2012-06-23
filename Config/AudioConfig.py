from ConfigBase import Config
from TreeNodes import *
from Formats import *
from DBInterface import DBInterface
from Aggregators import *
from Table import *

class AudioConfig(Config):

    
    # Audio Tags
    AudioTags = ("title", "artist", "album", "year", "genre", "track")

    # Audio primary
    AudioPrimary = "filename"
    AudioFormat  = "format"

    def __init__(self):
        columns = [Column("title"),
                   Column("artist"),
                   Column("album"),
                   Column("year"),
                   Column("genre"),
                   Column("track"),
                   Column("format",readonly=1),
                   Column("filename",readonly=1)]
        
        self.mainTable = MainTable(format="format",
                                   name="AudioInfo",
                                   columns=columns,
                                   primary="filename")
        
        self.tables = [self.mainTable]
        Config.__init__(self)

        # No auxiliary tables in AudioConfig
    
    def makeTree(self):
        db = DBInterface(self, self.dbname)
        table = "AudioInfo"
        songDefault = FileNode(table, "title", db, TrackTitleFormatConverter(table) )
        songSpecials = None
        songTree   = DBNode("song",
                            table,
                            "title",
                            db,
                            TrackTitleFormatConverter(table),
                            songDefault,
                            songSpecials )
        
        albumDefault = songTree
        albumSpecials = None
        albumTree = DBNode("album",
                           table, 
                           "album",
                            db,
                           SimpleFormatConverter(table, "album"),
                           albumDefault,
                           albumSpecials )
        
        artistDefault = albumTree
        artistSpecials = None
        artistTree = DBNode("artist",
                            table, 
                            "artist",
                            db,
                            SimpleFormatConverter(table, "artist"),
                            artistDefault,
                            artistSpecials )
        
        timeDefault = artistTree
        timeSpecials = None
        timeTree   = DBNode("time",
                            table, 
                            "year",
                            db,
                            SimpleFormatConverter(table, "year"),
                            timeDefault,
                            timeSpecials )
        timeAggregateSpecials = {"Unknown":timeDefault,
                                 "0" : timeDefault };
        timeAggregate = DBAggregateNode("time_aggregator",
                                        table, 
                                        "year",
                                        db,
                                        DecadeAggregator(),
                                        DecadeConverter(table, "year"),
                                        timeTree,
                                        timeAggregateSpecials )
        
        genreDefault = artistTree
        genreSpecials = { "Soundtrack":albumTree }
        genreTree  = DBNode("genre",
                            table, 
                            "genre",
                            db,
                            SimpleFormatConverter(table, "genre"),
                            genreDefault,
                            genreSpecials )
        
        allSongDefault = FileNode(table, "title", db, ArtistTitleFormatConverter(table) )
        allSongSpecials = None
        allSongTree = DBNode("song",
                             table, 
                             "title",
                             db,
                             ArtistTitleFormatConverter(table),
                             allSongDefault,
                             allSongSpecials )
        allSongTreeSpecials = None
        allSongAggregate = DBAggregateNode("song",
                                           table, 
                                           "title",
                                           db,
                                           FirstDigitAggregator(),
                                           AlphabeticalConverter(table, "title"),
                                           allSongTree,
                                           allSongTreeSpecials )
        
        basedict = {}
        basedict["ByGenre"] = genreTree
        basedict["ByArtist"] = artistTree
        ##########################################
        # Use this to not have a year sort
        #basedict["ByTime"] = timeTree
        ##########################################
        basedict["ByTime"] = timeAggregate
        
        ##########################################
        # Use this to not have an alphabetical sort
        # basedict["BySong"] = allSongTree
        ##########################################
        basedict["BySong"] = allSongAggregate

        self.tree = BaseNode( basedict )
            
    def getTree(self):
        if ( self.tree is None ):
            self.makeTree()
        return self.tree


_tmp = AudioConfig()


