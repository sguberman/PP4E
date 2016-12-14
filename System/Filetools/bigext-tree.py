"""
Find the largest file of a given type in an arbitrary directory tree.
Avoid repeat paths, catch errors, add tracing and line count size.
Also uses sets, file iterators, and generators to avoid loading entire
file, and attempts to work around undecodable dir/file name prints.
"""

import os, pprint
from sys import argv, exc_info


trace = 1  # 0=off, 1=dirs, 2=dirs+files
dirname, extname = os.curdir, '.py'  # default to cwd and .py files
if len(argv) > 1:
    dirname = argv[1]  # ex: C:\, C:\Python31\Lib
if len(argv) > 2:
    extname = argv[2]  # ex: .pyw, .txt
if len(argv) > 3:
    trace = int(argv[3])  # ex: ". .py 2"


def tryprint(arg):  # needed for handling unencodable filenames
    try:
        print(arg)
    except UnicodeEncodeError:
        print(arg.encode())


visited = set()
allsizes = []
for (directory, subdirs, files) in os.walk(dirname):
    if trace:
        tryprint(directory)
    directory = os.path.normpath(directory)
    fixname = os.path.normcase(directory)
    if fixname in visited:
        if trace:
            tryprint('skipping ' + directory)
    else:
        visited.add(fixname)
        for filename in files:
            if filename.endswith(extname):
                if trace > 1:
                    tryprint('+++' + filename)
                fullname = os.path.join(directory, filename)
                try:
                    bytesize = os.path.getsize(fullname)
                    linesize = sum(1 for line in open(fullname, 'rb'))
                except Exception:
                    print('error', exc_info()[0])
                else:
                    allsizes.append((bytesize, linesize, fullname))

for (title, key) in [('bytes', 0), ('lines', 1)]:
    print('\nBy %s...' % title)
    allsizes.sort(key=lambda x: x[key])
    pprint.pprint(allsizes[:3])
    pprint.pprint(allsizes[-3:])
