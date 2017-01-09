# pack text files into a single file with separator lines

import glob
import sys


marker = ':' * 20 + 'textpak=>'


def pack(ofile, ifiles):
    with open(ofile, 'w') as output:
        for name in ifiles:
            print('Packing:', name)
            input = open(name, 'r').read()
            if input[-1] != '\n':
                input += '\n'
            output.write(marker + name + '\n')
            output.write(input)


if __name__ == '__main__':
    ifiles = []
    for patt in sys.argv[2:]:
        ifiles += glob.glob(patt)
    pack(sys.argv[1], ifiles)
