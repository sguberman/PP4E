import shelve


with shelve.open('class-shelve') as db:
    sue = db['sue']
    sue.give_raise(.25)
    db['sue'] = sue

    tom = db['tom']
    tom.give_raise(.20)
    db['tom'] = tom
