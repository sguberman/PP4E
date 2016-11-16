import pickle
from initdata import db


with open('people-pickle', 'wb') as dbfile:
    pickle.dump(db, dbfile)
