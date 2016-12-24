import sys
from tkinter import *

sys.path.append('/home/seth/PycharmProjects/')
from PP4E.launchmodes import PortableLauncher


demoModules = ['demoDlg', 'demoRadio', 'demoCheck', 'demoScale']

for demo in demoModules:
    PortableLauncher(demo, demo + '.py')()

root = Tk()
root.title('Processes')
Label(root, text='Multiple program demo: commandlines', bg='white').pack()
root.mainloop()
