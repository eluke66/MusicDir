class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

# Returns a tag loader for the given file extension
class TagLoaderFactory:
    ExtensionMap = {}
    
    def GetLoader(filename):
        try:
            # Get the file extension
            parts = filename.split(".")
            if (len(parts) < 2):
                raise Exception("name " + filename)
            extension = parts[ len(parts) - 1 ].lower()
            if ( TagLoaderFactory.ExtensionMap.has_key(extension) ):
                return TagLoaderFactory.ExtensionMap[extension]
            else:
                raise Exception("extension " + extension)
        except Exception, e:
            #print "No tag loader for file",e
            return None

    def Register(loader, extensionlist):
        for extension in (extensionlist):
            TagLoaderFactory.ExtensionMap[extension.lower()] = loader

    GetLoader = Callable(GetLoader)
    Register = Callable(Register)
    

class TagLoader:

    # Register us with the tag loading factory
    def __init__(self,extensions):
        TagLoaderFactory.Register(self,extensions)

    # Gets tags from the given filename
    # Implemented by subclasses.
    def getTags(self,filename):
        print "Tag loader",self,"doesn't implement getTags()!"
        exit(-1)

    # Utility used by subclasses to ensure that all needed tags
    # are present in the tag list (returned by gettags)
    def fillTags(self,tagsNeeded,tagFilters,tags,filename):
        for tag in (tagsNeeded):
            if (not tags.has_key(tag) or tags[tag] == ""):
                tags[tag] = "Unknown"

        # Filter tags
        for tag in (tagsNeeded):
            if ( tagFilters.has_key(tag) ):
                filter = tagFilters[tag]
                # If we find a variant...
                if ( filter.keys().count(tags[tag]) > 0 ):
                    # Replace the variant with the canonical value
                    tags[tag] = filter[tags[tag]]
        tags["filename"] = filename
        tags["format"] = filename[filename.rindex(".")+1:].lower()

        # Clean up tags - ensure that there is no extra whitespace
        # around the tags
        for tag in tags.keys():
            tags[tag] = tags[tag].strip()
            
        return tags
                


