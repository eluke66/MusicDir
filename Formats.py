from DBValue import *

# Top level format converter interface
class FormatConverter:
    def __init__(self,format,table):
        self.format = format
        self.tags = []
        self.table = table
        items = format.split("%")
        for i in range(1,len(items)-1,2):
            self.tags.append( (items[i],self.table) )
            
    # Returns a list of tags needed from the DB
    # by this format
    def getTags(self):
        return self.tags

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
        
    # Input: DB Entry tags
    # Output: File name
    def formatToName(self,entry):
        file = self.format

        for tag in entry.keys():
            # DEBUG print "\t",tag[0],"\t",entry[tag],self.formatTag(entry[tag])
            file = file.replace("%"+tag[0]+"%", self.formatTag(entry[tag]))
        return file

    # Input: File name
    # Output : DB Entry tags
    def nameToFormat(self,db,name,currentSelect):
        raise UnimplementedException()

    def _findEntry(self,db,tags):
        entries = db.getEntries( tags, [("filename",self.table)], True )
        if ( len(entries) > 1 ):
            print "too many db entries (%d)" % (len(entries))
        if ( len(entries) == 0 ):
            print "ACH! No entries!"
            return None

        entry = (entries.pop())[0].encode("latin-1")
        return entry
                  
    def getPathBottom(self,path):
        # Return everything up to and including the first "/"
        # as top, and then the rest
        index = path.rfind("/")+1
        if ( index == 0 ):
            return path,""
        return path[index:], path[0:index]

#
# Simple format converter - the output is simply
# filling in the given tag. Suitable for albums,
# artists, etc.
#
# Ex: giving a tag of "album" will return
#     the value of the "album" tag
class SimpleFormatConverter(FormatConverter):
    def __init__(self,table,tag):
        FormatConverter.__init__(self, "%"+tag+"%",table)
        self.tag = tag
    
    def nameToFormat(self,db,name,currentSelect):
        # We just care about the filename
        file,dir = self.getPathBottom(name)
        tags = currentSelect
        tags.append( SimpleDBValue(file, self.table, self.tag) )
        return self._findEntry(db,tags)


class AlphabeticalConverter(FormatConverter):
    def __init__(self,table,tag):
        FormatConverter.__init__(self, "%"+tag+"%",table)
        self.tag = tag

    def getDBValue(self,path):
        path = path.rstrip("/")
        return LikeDBValue(path + "%",self.table,self.tag)
    
    def nameToFormat(self,db,name,currentSelect):
        # We just care about the filename
        file,dir = self.getPathBottom(name)
        tags = currentSelect
        tags.append( LikeDBValue(file + "%", self.table, self.tag) )
        return self._findEntry(db,tags)

class DecadeConverter(FormatConverter):
    def __init__(self,table,tag):
        FormatConverter.__init__(self, "%"+tag+"%",table)
        self.tag = tag
        
    # Input: Path variable
    # Output: DBValue entry
    def getDBValue(self,path):
        path = path.rstrip('/')
        if (path[-1] == 's'): # Decade!
            path = path[0:-1] # Remove 's'
            pmin = int(path)
            pmax = int(path) + 9
            return MinMaxDBValue(pmin,pmax,self.table,self.tag)

        # Otherwise, we need to get things with invalid years!
        return MultiDBValue(["Unknown","0","''"],self.table,self.tag)
    
    def nameToFormat(self,db,name,currentSelect):
        # We just care about the filename
        file,dir = self.getPathBottom(name)
        tags = currentSelect
        tags.append( MinMaxDBValue(file + "%", self.table, self.tag) )
        for t in tags:
            print str(t)
        return self._findEntry(db,tags)

#
# Creates a file including a track number, a title, and a
# format specification. Suitable for songs sorted by album.
#
class TrackTitleFormatConverter(FormatConverter):
    def __init__(self, table):
       FormatConverter.__init__(self, "%track% - %title%.%format%",table)

    def nameToFormat(self,db,name,currentSelect):
        # We just care about the filename
        file,dir = self.getPathBottom(name)

        # The part we care about is between the first '- ' and the last .
        start = file[file.find("- ") + len("- "):]
        title = start[0:start.rfind(".")]

        tags = currentSelect
        tags.append(SimpleDBValue(title,self.table,"title"))
        
        # We require format as well!
        # Otherwise, mp3fs uses us as a "pass through", thinking it's really
        # an mp3 (because we report that the mp3 is a real file, when it's
        # really a FLAC, for example).
        tags.append(SimpleDBValue(start[start.rfind(".")+1:],
                                  self.table,
                                  "format"))

        # If the track is specified, add that in too.
        track = file[0:file.find(" -")]
        if ( track != "Unknown" ):
            tags.append(SimpleDBValue(track, self.table, "track"))
        
        
        return self._findEntry(db,tags)

#
# Creates a file featuring the title, with the
# artist also included.
class ArtistTitleFormatConverter(FormatConverter):
    def __init__(self, table):
        FormatConverter.__init__(self, "%title% (by %artist%).%format%",table)
        

    def nameToFormat(self,db,name,currentSelect):
        # We just care about the filename
        file,dir = self.getPathBottom(name)

        # The part we care about is between the first '- ' and the last .
        end = file.find("(by ") - 1
        title = file[0:end]

        tags = currentSelect
        tags.append(SimpleDBValue(title, self.table, "title" ))

        # Grab the artist
        astart = end+5
        aend = file.rfind(").")
        artist = file[astart:aend]
        tags.append(SimpleDBValue(artist,self.table,"artist"))

        # We require format as well!
        # Otherwise, mp3fs uses us as a "pass through", thinking it's really
        # an mp3 (because we report that the mp3 is a real file, when it's
        # really a FLAC, for example).
        tags.append(SimpleDBValue(file[file.rfind(".")+1:],
                                  self.table,
                                  "format"))
        return self._findEntry(db,tags)

######################################################
#
# Creates a file including a title, and a format specification.
#
class TitleFormatConverter(FormatConverter):
    def __init__(self,table):
       FormatConverter.__init__(self, "%title%.%format%",table)

    def nameToFormat(self,db,name,currentSelect):
        # We just care about the filename
        file,dir = self.getPathBottom(name)

        # Title is everything up to the final "."
        title = file[0:file.rfind(".")]

        tags = currentSelect
        tags.append(SimpleDBValue(title,self.table,"title"))
        tags.append(SimpleDBValue(file[file.rfind(".")+1:],
                                  self.table,
                                  "format"))

        return self._findEntry(db,tags)


######################################################
#
# Creates a file ID and format 
#
class IDFormatConverter(FormatConverter):
    def __init__(self,table):
       FormatConverter.__init__(self, "%ID%.%format%",table)

    def nameToFormat(self,db,name,currentSelect):
        # We just care about the filename
        file,dir = self.getPathBottom(name)

        # Title is everything up to the final "."
        title = file[0:file.rfind(".")]

        tags = currentSelect
        tags.append(SimpleDBValue(title, self.table, "ID"))
        tags.append(SimpleDBValue(file[file.rfind(".")+1:],
                                  self.table,
                                  "format"))

        return self._findEntry(db,tags)

