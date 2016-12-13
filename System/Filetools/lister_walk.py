import sys, os


def lister(root):
    for (dirname, subdirs, filenames) in os.walk(root):
        print('[' + dirname + ']')
        for fname in filenames:
            path = os.path.join(dirname, fname)
            print(path)


if __name__ == '__main__':
    lister(sys.argv[1])
