from Config import *
from TagLoader import *

TagFilters = {}

PictureTags = PictureConfig.PictureTags

class PictureTagLoader(TagLoader):
    extensions = ("jpg","jpeg","gif","png")

    
    def __init__(self):
        TagLoader.__init__(self,PictureTagLoader.extensions)

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

    def getTags(self, filename):
        tags = {}
        
        q = self.fillTags(PictureTags,TagFilters,tags,filename)
        print q
        return q

pictagloader = PictureTagLoader()
