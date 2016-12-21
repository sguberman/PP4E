"""
##############################################################################
Count lines among all program source files in a tree named on the command
line, and report totals grouped by file types (extension). A simple SLOC
(source lines of code) metric: skip blank and comment lines if desired.
"""

import os
import pprint
import sys

from visitor import FileVisitor


class LinesByType(FileVisitor):
    srcexts = []  # define in subclass

    def __init__(self, trace=1):
        FileVisitor.__init__(self, trace=trace)
        self.srclines = self.srcfiles = 0
        self.extsums = {ext: dict(files=0, lines=0) for ext in self.srcexts}

    def visitsource(self, fpath, ext):
        if self.trace > 0:
            print(os.path.basename(fpath))
        lines = len(open(fpath, 'rb').readlines())
        self.srcfiles += 1
        self.srclines += lines
        self.extsums[ext]['files'] += 1
        self.extsums[ext]['lines'] += lines

    def visitfile(self, filepath):
        FileVisitor.visitfile(self, filepath)
        for ext in self.srcexts:
            if filepath.endswith(ext):
                self.visitsource(filepath, ext)
                break


class PyLines(LinesByType):
    srcexts = ['.py', '.pyw']


class SourceLines(LinesByType):
    srcexts = ['.py', '.pyw', '.cgi', '.html', '.c', '.cxx', '.h', '.i']


if __name__ == '__main__':
    walker = SourceLines()
    walker.run(sys.argv[1])
    print('Visited %d files and %d dirs' % (walker.fcount, walker.dcount))
    print('-' * 80)
    print('Source files=>%d, lines=>%d' % (walker.srcfiles, walker.srclines))
    print('By Types:')
    pprint.pprint(walker.extsums)

    print('\nCheck sums:', end=' ')
    print(sum(x['lines'] for x in walker.extsums.values()), end=' ')
    print(sum(x['files'] for x in walker.extsums.values()))

    print('\nPython only walk:')
    walker = PyLines(trace=0)
    walker.run(sys.argv[1])
    pprint.pprint(walker.extsums)
