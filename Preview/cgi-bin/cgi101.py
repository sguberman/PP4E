#!/usr/bin/python
import cgi, html


form = cgi.FieldStorage()
print('Content-type: text/html\n')
print('<title>Reply Page</title>')
if 'user' not in form:
    print('<h1>Who are you?</h1>')
else:
    print('<h1>Hello <i>{}</i>!'.format(html.escape(form['user'].value)))
