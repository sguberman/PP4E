import pickle
from initdata import bob, sue, tom


for (key, record) in [('bob', bob), ('tom', tom), ('sue', sue)]:
    with open(key + '.pkl', 'wb') as recfile:
        pickle.dump(record, recfile)
