import sys


def filter_files(name, function):
    with open(name, 'r') as inp, open(name + '.out', 'w') as out:
        for line in inp:
            out.write(function(line))


def filter_stream(function):
    for line in sys.stdin:
        print(function(line), end='')


if __name__ == '__main__':
    filter_stream(lambda line: line)
