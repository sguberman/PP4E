"""
##############################################################################
Return all files matching a filename pattern at and below a root directory.
"""

import fnmatch, os


def find(pattern, startdir=os.curdir):
    for (directory, subdirs, filedirs) in os.walk(startdir):
        for name in subdirs + filedirs:
            if fnmatch.fnmatch(name, pattern):
                fullpath = os.path.join(directory, name)
                yield fullpath


def findlist(pattern, startdir=os.curdir, dosort=False):
    matches = list(find(pattern, startdir))
    if dosort:
        matches.sort()
    return matches


if __name__ == '__main__':
    import sys
    namepattern, startdir = sys.argv[1], sys.argv[2]
    for name in find(namepattern, startdir):
        print(name)
