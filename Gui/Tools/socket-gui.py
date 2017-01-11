# GUI server side: read and display non-GUI script's output

import sys
import os
from socket import *
from tkinter import Tk

from PP4E.launchmodes import PortableLauncher
from PP4E.Gui.Tools.guiStreams import GuiOutput


myport = 50008
sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.bind(('', myport))
sockobj.listen(5)

print('starting')
PortableLauncher('nongui', 'socket-nongui.py -gui')()

print('accepting')
conn, addr = sockobj.accept()
conn.setblocking(False)
print('accepted')


def checkdata():
    try:
        message = conn.recv(1024)
        print(message, file=output)
    except error:
        print('no data')
    root.after(1000, checkdata)


root = Tk()
output = GuiOutput(root)
checkdata()
root.mainloop()
