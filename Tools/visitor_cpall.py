"""
##############################################################################
Use: "python ...\Tools\visitor_cpall.py fromdir todir trace?"
Like System\Filetools\cpall.py, but with the visitor classes and os.walk;
does string replacement of fromdir with todir at the front of all the names
that the walker passes in; assumes that the todir does not exist initially.
"""
import os
import sys

sys.path.append(os.getcwd())
from visitor import FileVisitor
from System.Filetools.cpall import copyfile


class CpallVisitor(FileVisitor):
    def __init__(self, fromdir, todir, trace=True):
        self.fromdirlen = len(fromdir)
        self.todir = todir
        FileVisitor.__init__(self, trace=trace)

    def visitdir(self, dirpath):
        topath = os.path.join(self.todir, dirpath[self.fromdirlen:])
        if self.trace:
            print('d', dirpath, '=>', topath)
        os.mkdir(topath)
        self.dcount += 1

    def visitfile(self, filepath):
        topath = os.path.join(self.todir, filepath[self.fromdirlen:])
        if self.trace:
            print('f', filepath, '=>', topath)
        copyfile(filepath, topath)
        self.fcount += 1


if __name__ == '__main__':
    import sys, time
    fromdir, todir = sys.argv[1:3]
    trace = len(sys.argv) > 3
    print('Copying...')
    start = time.clock()
    walker = CpallVisitor(fromdir, todir, trace)
    walker.run(startdir=fromdir)
    print('Copied', walker.fcount, 'files,', walker.dcount, 'directories', end=' ')
    print('in', time.clock() - start, 'seconds')
