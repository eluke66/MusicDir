from musicfs import *

dirs = ["ByGenre", "ByArtist", "ByTime", "BySong"]
tags = ["genre", "artist", "year", "title"]

songTree   = [("song", "title")]
albumTree  = [("album","album")]
albumTree.extend(songTree)
artistTree = [("artist","artist")]
artistTree.extend(albumTree)
timeTree = [("time","year")]
timeTree.extend(artistTree)
genreTree = [("genre","genre")]
genreTree.extend(artistTree)

subnodes = [genreTree, artistTree, timeTree, songTree]
base = BaseNode(dirs,tags,subnodes)
#print processTree("/",base,Node.GetAttr)
#print processTree("/",base,Node.ReadDir)
#print processTree("/ByGenre",base,Node.GetAttr)
#print processTree("/ByGenre",base,Node.ReadDir)
#print processTree("/ByGenre/",base,Node.GetAttr)
#print processTree("/ByGenre/",base,Node.ReadDir)
#print processTree("/BySong",base,Node.ReadDir)
#print processTree("/BySong/Zum",base,Node.GetAttr)
#print processTree("/BySong/Zombie Jamboree",base,Node.GetAttr)
#print processTree("/ByArtist/",base,Node.ReadDir)
#print processTree("/ByArtist/billy joel/",base,Node.ReadDir)
print processTree("/ByArtist/billy joel/",base,Node.GetAttr)
#print processTree("/ByArtist/billy joel/All Time Greatest Movie Songs",base,Node.ReadDir)
print processTree("/ByArtist/billy joel/All Time Greatest Movie Songs/Modern Woman",base,Node.GetAttr)
