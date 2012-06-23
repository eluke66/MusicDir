from Config import *
from TagLoader import *

TagFilters = {}

VideoTags = VideoConfig.VideoTags

class VideoTagLoader(TagLoader):
    extensions = ("mpg","mpeg","avi","wmv","mov","iso")

    def __init__(self):
        TagLoader.__init__(self,VideoTagLoader.extensions)

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
        
        ########################
        # Temp for now!
        import os.path
        t = os.path.basename(filename)
        tags["title"] = t[0:t.rfind(".")]
        #########################
        
        q = self.fillTags(VideoTags,TagFilters,tags,filename)
        print q
        return q

vidtagloader = VideoTagLoader()
