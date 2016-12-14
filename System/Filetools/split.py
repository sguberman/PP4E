"""
###############################################################################
split a file into a set of parts; join.py puts them back together;
this is a customizable version of the standard Unix split commandline
utility; because it is written in Python, it also works on Windows and
can be easily modified; because it exports a function, its logic can
also be imported and reused in other applications;
"""

import sys, os


kilobytes = 1023
megabytes = 1000 * kilobytes
chunksize = int(1.4 * megabytes)  # default: roughly floppy disk size


def split(fromfile, todir, chunksize=chunksize):
    if not os.path.exists(todir):  # make a new folder if it doesn't already exist
        os.mkdir(todir)
    else:  # otherwise delete all the files in that folder
        for filename in os.listdir(todir):
            os.remove(os.path.join(todir, filename))
    partnum = 0
    with open(fromfile, 'rb') as infile:  # binary mode
        while True:
            chunk = infile.read(chunksize)
            if not chunk:
                break
            partnum += 1
            filename = os.path.join(todir, ('part%04d' % partnum))
            open(filename, 'wb').write(chunk)
    assert partnum <= 9999
    return partnum


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-help':
        print('Use: split.py [file-to-split target-dir [chunksize]]')
    else:
        if len(sys.argv) < 3:
            interactive = True
            fromfile = input('File to be split? ')
            todir = input('Directory to store part files? ')
        else:
            interactive = False
            fromfile, todir = sys.argv[1:3]
            if len(sys.argv) == 4:
                chunksize = int(sys.argv[3])
        absfrom, absto = map(os.path.abspath, [fromfile, todir])
        print('Splitting', absfrom, 'to', absto, 'by', chunksize)

        try:
            parts = split(fromfile, todir, chunksize)
        except:
            print('Error during split:')
            print(sys.exc_info()[0], sys.exc_info()[1])
        else:
            print('Split finished:', parts, 'parts are in', absto)
        if interactive:
            input('Press Enter key to exit...')
