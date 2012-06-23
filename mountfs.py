#!/bin/env python

import fuse, os, sys
from fuse import Fuse
from Config import *
from DBInterface import *
import TreeNodes

fuse.fuse_python_api = (0, 2)

fuse.feature_assert('stateful_files', 'has_init')

GlobalConfig = None

def flag2mode(flags):
    md = {os.O_RDONLY: 'r', os.O_WRONLY: 'w', os.O_RDWR: 'w+'}
    m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        m = m.replace('w', 'a', 1)

    return m

class MusicFS(Fuse):
    def __init__(self, *args, **kw):

        # Pull DB arg out of keywords
        if ( kw.has_key("db") ):
            self.dbname = kw["db"]
            del kw["db"]
            
        Fuse.__init__(self, *args, **kw)

        # do stuff to set up your filesystem here, if you want
        #import thread
        #thread.start_new_thread(self.mythread, ())
        self.root = '/'

    def getattr(self, path):
        print "GETATTR -%s-"%path
        return TreeNodes.processTree(path,self.config.getTree(),TreeNodes.Node.GetAttr,[])

    def readlink(self, path):
        print "READLINK -%s-"%path
        return os.readlink("." + path)
    
    def readdir(self, path, offset):
        print "READING DIR",path
        items = TreeNodes.processTree(path,self.config.getTree(),TreeNodes.Node.ReadDir,[])
        for item in items:
            if ( item != "" ):
                yield fuse.Direntry(item)

    def unlink(self, path):
        pass

    def rmdir(self, path):
        pass

    def symlink(self, path, path1):
        pass

    def rename(self, path, path1):
        pass

    def link(self, path, path1):
        pass
        
    def chmod(self, path, mode):
        pass

    def chown(self, path, user, group):
        pass

    def truncate(self, path, len):
        pass

    def mknod(self, path, mode, dev):
        pass

    def mkdir(self, path, mode):
        pass

    def utime(self, path, times):
        pass

    def access(self, path, mode):
        print "ACCESS -%s-"%path
        if not os.access("." + path, mode):
            return -EACCES

    def statfs(self):
        """
        Should return an object with statvfs attributes (f_bsize, f_frsize...).
        Eg., the return value of os.statvfs() is such a thing (since py 2.2).
        If you are not reusing an existing statvfs object, start with
        fuse.StatVFS(), and define the attributes.

        To provide usable information (ie., you want sensible df(1)
        output, you are suggested to specify the following attributes:

            - f_bsize - preferred size of file blocks, in bytes
            - f_frsize - fundamental size of file blcoks, in bytes
                [if you have no idea, use the same as blocksize]
            - f_blocks - total number of blocks in the filesystem
            - f_bfree - number of free blocks
            - f_files - total number of file inodes
            - f_ffree - nunber of free file inodes
        """

        return os.statvfs(".")

    def fsinit(self):
        try:
            global GlobalConfig
            self.config = ConfigFactory.GetConfigByTable( GetDBTable( self.dbname ) )
            self.config.setDB( self.dbname )
            GlobalConfig = self.config
        
            if ( self.dbname is None ):
                self.db = DBInterface(self.config)
            else:
                self.db = DBInterface(self.config, self.dbname)
        except Exception,e:
            print "Caught exception in FSINIT:",e

    class MusicFSFile(object):

        def __init__(self, path, flags, *mode):
            print "**********************XXXXXXXXXXXXX MUSICFSFILE **************"
            realFile = TreeNodes.processTree(path,GlobalConfig.getTree(),TreeNodes.Node.LookupFile,[])
            self.file = os.fdopen(os.open(realFile, flags, *mode),
                                  flag2mode(flags))
            self.fd = self.file.fileno()

        def read(self, length, offset):
            self.file.seek(offset)
            return self.file.read(length)

        def write(self, buf, offset):
            # Not implemented
            return 0

        def release(self, flags):
            self.file.close()

        def fsync(self, isfsyncfile):
            if isfsyncfile and hasattr(os, 'fdatasync'):
                os.fdatasync(self.fd)
            else:
                os.fsync(self.fd)

        def flush(self):
            os.close(os.dup(self.fd))

        def fgetattr(self):
            return os.fstat(self.fd)

        def ftruncate(self, len):
            self.file.truncate(len)

    def main(self, *a, **kw):

        self.file_class = self.MusicFSFile
        return Fuse.main(self, *a, **kw)


def main():

    usage = """
Userspace nullfs-alike: mirror the filesystem tree from some point on.

""" + Fuse.fusage

    # DUMB WAY TO DO THIS
    argv = []
    init = 0
    theDB = None
    for item in sys.argv:
        if ( item == "-db" ):
            init = 1
        elif ( init == 1 ):
            theDB = item
            init = 0
        else:
            argv.append(item)
    sys.argv = argv
    # END OF DUMB WAY
    
    server = MusicFS(version="%prog " + fuse.__version__,
                 usage=usage,
                 db=theDB,
                 dash_s_do='setsingle')

    server.parser.add_option(mountopt="root", metavar="PATH", default='/',
                             help="mirror filesystem from under PATH [default: %default]")

    server.parse(values=server, errex=1)

    try:
        if server.fuse_args.mount_expected():
            os.chdir(server.root)
    except OSError:
        print >> sys.stderr, "can't enter root of underlying filesystem"
        sys.exit(1)

    server.main()


if __name__ == '__main__':
    main()
