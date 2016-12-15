"""
##############################################################################
Usage: "python ...\Tools\visitor_replace.py rootdir fromstr tostr"
Does global search-and-replace in all files in a directory tree: replaces
fromstr with tostr in all text files; this is powerful but dangerous!
use visitor_collect.py to simply collect matched files list; listonly mode
here is similar to both SearchVisitor and CollectVisitor;
"""

import sys

from visitor import SearchVisitor


class ReplaceVisitor(SearchVisitor):
    """
    Change fromstr to tostr in files at and below startdir;
    files changed available in obj.changed list after a run.
    """
    def __init__(self, fromstr, tostr, listonly=False, trace=0):
        self.changed = []
        self.tostr = tostr
        self.listonly = listonly
        SearchVisitor.__init__(self, fromstr, trace)

    def visitmatch(self, fname, text):
        self.changed.append(fname)
        if not self.listonly:
            fromstr, tostr = self.context, self.tostr
            text = text.replace(fromstr, tostr)
            open(fname, 'w').write(text)


if __name__ == '__main__':
    listonly = input('List only?') == 'y'
    visitor = ReplaceVisitor(sys.argv[2], sys.argv[3], listonly)
    if listonly or input('Proceed with changes?') == 'y':
        visitor.run(startdir=sys.argv[1])
        action = 'Changed' if not listonly else 'Found'
        print('Visited %d files' % visitor.fcount)
        print(action, '%d files:' % len(visitor.changed))
        for fname in visitor.changed:
            print(fname)
