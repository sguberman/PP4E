def scanner(name, function):
    with open(name, 'r') as file:
        for line in file:
            function(line)
