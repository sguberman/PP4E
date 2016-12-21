"""
##############################################################################
Usage: "python cpall.py fromdir todir"
Recursive copy of a directory tree. Works like a "cp -r fromdir/* todir"
Unix command, and assumes that fromdir and todir are both directories.
"""

import os, sys


maxfileload = 1000000
blksize = 1024 * 500


def copyfile(frompath, topath, maxfileload=maxfileload):
    """
    Copy one file, byte for byte;
    use binary file modes to suppress Unicode decode and endline transform.
    """
    if os.path.getsize(frompath) <= maxfileload:
        bytesfrom = open(frompath, 'rb').read()
        open(topath, 'wb').write(bytesfrom)
    else:
        with open(frompath, 'rb') as fromfile, open(topath, 'wb') as tofile:
            while True:
                bytesfrom = fromfile.read(blksize)
                if not bytesfrom:
                    break
                tofile.write(bytesfrom)


def copytree(fromdir, todir, verbose=0):
    """
    Copy contents of fromdir and below to todir, return (files, dirs) counts;
    may need to use bytes for dirnames if undecodable on other platforms;
    may need to do more file type checking on Unix: skip links, fifos, etc.
    """
    fcount = dcount = 0
    for filename in os.listdir(fromdir):
        frompath = os.path.join(fromdir, filename)
        topath = os.path.join(todir, filename)
        if not os.path.isdir(frompath):
            try:
                if verbose > 1:
                    print('copying', frompath, 'to', topath)
                copyfile(frompath, topath)
                fcount += 1
            except:
                print('Error copying', frompath, 'to', topath, '--skipped')
                print(sys.exc_info()[0], sys.exc_info()[1])
        else:
            if verbose:
                print('copying dir', frompath, 'to', topath)
            try:
                os.mkdir(topath)
                below = copytree(frompath, topath)
                fcount += below[0]
                dcount += below[1]
                dcount += 1
            except:
                print('Error creating', topath, '--skipped')
                print(sys.exc_info()[0], sys.exc_info()[1])
    return (fcount, dcount)


def getargs():
    """
    Get and verify directory name arguments;
    return default None on errors.
    """
    try:
        fromdir, todir = sys.argv[1:]
    except:
        print('Usage error: cpall.py fromdir todir')
    else:
        if not os.path.isdir(fromdir):
            print('Error: fromdir is not a directory')
        elif not os.path.exists(todir):
            os.mkdir(todir)
            print('Note: todir was created')
            return (fromdir, todir)
        else:
            print('Warning: todir alread exists')
            if hasattr(os.path, 'samefile'):
                same = os.path.samefile(fromdir, todir)
            else:
                same = os.path.abspath(fromdir) == os.path.abspath(todir)
            if same:
                print('Error: fromdir same as todir')
            else:
                return (fromdir, todir)


if __name__ == '__main__':
    import time
    dirstuple = getargs()
    if dirstuple:
        print('Copying...')
        start = time.clock()
        fcount, dcount = copytree(*dirstuple)
        print('Copied', fcount, 'files', dcount, 'directories', end=' ')
        print('in', time.clock() - start, 'seconds')
