import glob
import pickle


for filename in glob.glob('*.pkl'):
    with open(filename, 'rb') as recfile:
        record = pickle.load(recfile)
        print(filename, '=>\n  ', record)
