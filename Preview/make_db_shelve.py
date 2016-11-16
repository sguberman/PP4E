import shelve
from initdata import bob, sue


with shelve.open('people-shelve') as db:
    db['bob'] = bob
    db['sue'] = sue
