import shelve
from initdata import tom


with shelve.open('people-shelve') as db:
    sue = db['sue']
    sue['pay'] *= 1.50
    db['sue'] = sue
    db['tom'] = tom
