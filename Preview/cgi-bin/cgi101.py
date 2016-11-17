#!/usr/bin/python
import cgi


form = cgi.FieldStorage()
print('Content-type: text/html\n')
print('<title>Reply Page</title>')
if 'user' not in form:
    print('<h1>Who are you?</h1>')
else:
    print('<h1>Hell <i>{}</i>!'.format(cgi.escape(form['user'].value)))
