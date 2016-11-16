# interactive updates
import shelve
from Preview.person_alternative import Person


fieldnames = ('name', 'age', 'job', 'pay')

with shelve.open('class-shelve') as db:
    while True:
        key = input('\nKey? => ')
        if not key:
            break
        if key in db:
            record = db[key]
        else:
            record = Person(name='?', age='?')
        for field in fieldnames:
            currval = getattr(record, field)
            newtext = input('\t[{}]={}\n\t\tnew?=>'.format(field, currval))
            if newtext:
                setattr(record, field, eval(newtext))
        db[key] = record
