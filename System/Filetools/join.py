"""
###############################################################################
join all parts of files in a dir created by split.py to recreate the orig file;
this is roughly like a 'cat fromdir/* > tofile' command on unix, but is more
portable and configurable and exports the join function for reusability; relies
on sort order of filenames (must be the same length); could extend split and
join to pop up Tkinter file selectors.
"""

import os, sys


readsize = 1024


def join(fromdir, tofile):
    with open(tofile, 'wb') as outfile:
        for filename in sorted(os.listdir(fromdir)):
            with open(os.path.join(fromdir, filename), 'rb') as infile:
                while True:
                    filebytes = infile.read(readsize)
                    if not filebytes:
                        break
                    outfile.write(filebytes)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-help':
        print('Use: join.py [from-dir-name to-file-name]')
    else:
        if len(sys.argv) != 3:
            interactive = True
            fromdir = input('Directory containing part files? ')
            tofile = input('Name of file to be recreated? ')
        else:
            interactive = False
            fromdir, tofile = sys.argv[1:]
        absfrom, absto = map(os.path.abspath, [fromdir, tofile])
        print('Joining', absfrom, 'to make', absto)

        try:
            join(fromdir, tofile)
        except:
            print('Error joining files:')
            print(sys.exc_info()[0], sys.exc_info()[1])
        else:
            print('Join complete: see', absto)
        if interactive:
            input('Press Enter key to exit')
