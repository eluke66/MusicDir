from Config import *
from TagLoader import *


GenreFilters = { "Folk-Rock":"Folk Rock", "General Rock":"Rock", "misc":"Miscellaneous", "R & B":"R&B",
                 "rock":"Rock", "Rock & Roll":"Rock",
                 "Sound track":"Soundtrack", "Sound Track":"Soundtrack", "soundtrack":"Soundtrack",
                 "Sublime RockNRoll":"Rock", "unknown":"Unknown"}

ArtistFilters = {
    "Alain Boublil & Claude-Michel Schönberg":"Alain Boublil & Claude-Michel Sch_nberg",
    "Alison Krause":"Alison Krauss",
    "Alison Krauss and Union Station":"Alison Krauss",
    "Alison Krauss + Union Station":"Alison Krauss",
    "Alison Krauss + Union Station,":"Alison Krauss",
    "Alison Kraus + Union Station":"Alison Krauss",
    "Allan sherman":"Allan Sherman",
    "Bill Haley And His Comets":"Bill Haley And The Comets",
    "Bill Haley & His Comets":"Bill Haley And The Comets",
    "Billy J Kramer & Dakotas":"Billy J. Kramer & the Dakotas",
    "billy joel":"Billy Joel",
    "Blood Sweat and Tears":"Blood, Sweat and Tears",
    "Booker T. & the MG's":"Booker T & the MGs",
    "Booker T & The MG's":"Booker T & the MGs",
    "Booker T. & The MG's":"Booker T & the MGs",
    "Brian Setzer Orchestra (The)":"Brian Setzer Orchestra",
    "D' Arienzo":"D'Arienzo",
    "Dave 'Baby' Cortez":"Dave Baby Cortez",
    "David Seville & the Chipmunks":"David Seville & The Chipmunks",
    "Diana Ross & the Supremes":"Diana Ross & The Supremes",
    "Dion & the Belmonts":"Dion & The Belmonts",   
    "Disneyland Chorus":"Disney Chorus",
    "Disney Orchestra & Chorus":"Disney Chorus",
    "DIO, Ronnie James":"Ronnie James Dio",
    "Faith no More":"Faith No More",
    "Friends of Distinction":"Friends Of Distinction",
    "Friends Of Distinction ":"Friends Of Distinction",
    "Gary Puckett  & the Union Gap":"Gary Puckett & The Union Gap",
    "Gary Puckett & the Union Gap":"Gary Puckett & The Union Gap",
    "Gerry & the Pacemakers":"Gerry & The Pacemakers",
    "Guns 'n' Roses":"Guns N' Roses",
    "Herman's Hermits":"Hermans Hermits",
    "Ike & Tina Turner":"Ike and Tina Turner",
    "Jack scott":"Jack Scott",
    "Jimmy Gilmer & the Fireballs":"Jimmy Gilmer & The Fireballs",
    "Joey Dee & the Starlighter":"Joey Dee & the Starlites",
    "Johnny Mathis [JS-VBR]":"Johnny Mathis",
    "Jr. Walker and The All Stars":"Jr. Walker & the All Stars",
    "juno reactor":"Juno Reactor",
    "Juno Reactor ":"Juno Reactor",
    "Juno Reactor Featuring Gocoo":"Juno Reactor",
    "Juno Reactor - Don Davis":"Juno Reactor & Don Davis",
    "Juno Reactor vs. Don Davis":"Juno Reactor & Don Davis",
    "Juno Reactor Vs Don Davis":"Juno Reactor & Don Davis",
    "Khachaturian, Aram":"Khachaturian",
    "Les Paul & Mary Ford":"Les Paul And Mary Ford",
    "Little Anthony & the Imperials":"Little Anthony And The Imperials",
    "Maria Carey":"Mariah Carey",
    "Marty Robbins":"Marty Robins",
    "MC Hawking (Dark Matter)":"MC Hawking",
    "Michael Buble             ":"Michael Buble",
    "michael jackson":"Michael Jackson",
    "Nat king cole": "Nat King Cole",
    "Naughty by Nature":"Naughty By Nature",
    "Neil Sekaka":"Neil Sedaka",
    "Original London Cast":"Original London Cast Recording",
    "Original London Cast recording":"Original London Cast Recording",
    "Paul Revere & the Raider":"Paul Revere & The Raiders",
    "Paul Revere & the Raiders":"Paul Revere & The Raiders",
    "rachmaninoff":"Rachmaninov",
    "Rodgers & Hammerstein": "Rogers And Hammerstein",
    "Sammy Davis Jr":"Sammy Davis, Jr.",
    "Sammy Davis Jr.":"Sammy Davis, Jr.",
    "Sam the Sham & the Pharaohs":"Sam The Sham & the Pharaohs",
    "Sergio Mendes & Brasil '66":"Sergio Mendez & Brazil '66",
    "Skip & Flip":"Skip And Flip",
    "Smokey Robinson and the Miracles":"Smokey Robinson & The Miracles",
    "Smokey Robinson & the Miracles":"Smokey Robinson & The Miracles",
    "The beach boys":"The Beach Boys",
    "The Godfather":"The Godfather Soundtrack",
    "Tim Eriksen: Riley Baugus":    "Tim Eriksen & Riley Baugus",
    "Tommy James & the Shondells":"Tommy James & The Shondells",
    "Tommy James & the Shondels":"Tommy James & The Shondells",
    "Vaughn Monroe":"Vaughn Monroe & His Orchestra",
    "Weird al":"Weird Al Yankovic",
    "Weird Al":"Weird Al Yankovic",
    "Weird Al Yankovich":"Weird Al Yankovic",
    }


    
TagFilters = {"genre":GenreFilters, "artist":ArtistFilters}

AudioTags = AudioConfig.AudioTags


##############################################
# Tag loader for MP3 files
class MP3TagLoader(TagLoader):

    # MP3 file extensions
    extensions = ("mp3",)

    # Initialize mp3 loader
    def __init__(self):
        try:
            import eyeD3
            TagLoader.__init__(self,MP3TagLoader.extensions)
        except ImportError:
            print "No eyeD3 module found - not registering MP3 tag loader"

    def formatTag(self,tag):
        if ( tag is None ):
            return ""
        elif ( isinstance(tag,int) ):
            return str(tag)
        elif ( isinstance(tag,str) ):
            return tag
        elif ( isinstance(tag,unicode) ):
            return tag.encode("latin-1")
        else:
            raise Exception("unknown tag type " + type(tag) )
        
    # Returns tags for the given file
    def getTags(self, filename):
        tags = {}
        import eyeD3
        tagMessage = ""
        try:
            id3info = eyeD3.Tag()
            id3info.link(filename)
            for tag in (AudioTags):
                if ( tag == "track"):
                    track = id3info.getTrackNum()
                    if (track is not None):
                        tags[tag] = track[0]
                elif (tag == "genre" ):
                    genre = None
                    try:
                        genre = id3info.getGenre()
                        if ( genre is not None ):
                            tags[tag] = genre.getName()
                        else:
                            tags[tag] = "unknown"
                    except eyeD3.GenreException,ge:
                        # Load genre string another way
                        tf = id3info.frames[eyeD3.GENRE_FID]
                        genre = tf[0].text
                        if ( genre is not None and genre != "" ):
                            tags["genre"] = genre
                        else:
                            tags["genre"] = "unknown"
                        
                else:
                    #print "GETTING",tag.title()
                    getter = "get"+tag.title()
                    #print "\t",getter
                    func = getattr(id3info,getter)
                    if ( func is None):
                        print "Huh - no func named",getter
                    tags[tag] = func()

                #print "\tTag",tag,tags[tag],type(tags[tag])

                hasTag = tags.has_key(tag) #and str(tags[tag]) != ""
                
                if (not hasTag and tag != "year" ):
                    tagMessage += "\tTag not set: "+tag+"\n"

                tags[tag] = self.formatTag(tags[tag])
                # Was - tags[tag] = str(tags[tag]).encode("latin-1")
                #tags[tag] = tags[tag].encode("latin-1")
        except eyeD3.tag.TagException,t:
            print "Error processing tags for",filename,":",t
        except eyeD3.tag.GenreException,g:
            print "Error processing genre for",filename,":",g
            
        #except Exception,e:
        #    print "Can't get ID3 tag info for file",filename,e,type(e)
        #    return None
        
        if ( tagMessage != "" ):
            print filename,"is missing the following tags:"
            print tagMessage
        return self.fillTags(AudioTags,TagFilters,tags,filename)
        
# The MP3 Tag loader
mp3tagloader = MP3TagLoader()
#################################################
# Tag loader for FLAC files
class FlacTagLoader(TagLoader):
    
    # flac file extensions
    extensions = ("flac",)
    FlacTags = ["title", "artist", "album", "date", "genre", "tracknumber"]
    
    # Initialize flac loader
    def __init__(self):
        try:
            from flac import metadata
            TagLoader.__init__(self,FlacTagLoader.extensions)
        except ImportError:
            print "No flac module found - not registering FLAC tag loader"

    # Returns tags for the given file
    def getTags(self, filename):
        tags = {}
        from flac import metadata 
        try:
            chain = metadata.Chain()
            chain.read(filename)
            it = metadata.Iterator()
            it.init(chain)
            while 1:
                block = it.get_block()
                if (block.type == metadata.VORBIS_COMMENT):
                    comment = block.data.vorbis_comment
                    for i in range(comment.num_comments):
                        tag,val = comment.comments[i].split("=")
                        # Find the tag in the list of tags we're looking for
                        if (FlacTagLoader.FlacTags.count(tag.lower()) > 0): 
                            tagindex = FlacTagLoader.FlacTags.index(tag.lower())
                            tags[ AudioTags[tagindex] ] = val
                if not it.next():
                    break
        except Exception,e:
            print "Can't get FLAC tag info for file",filename,e
            return None
        return self.fillTags(AudioTags,TagFilters,tags,filename)
        
# The FLAC Tag loader
flactagloader = FlacTagLoader()

