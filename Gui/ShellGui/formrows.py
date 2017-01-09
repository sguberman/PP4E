"""
create a label+entry row frame, with optional file open browse button;
this is a separate module because it can save code in other programs too;
caller (or callbacks here): retain returned linked var while row is in use;
"""

from tkinter import *
from tkinter.filedialog import askopenfilename


def makeFormRow(parent, label, width=15, browse=True, extend=False):
    var = StringVar()
    row = Frame(parent)
    lab = Label(row, text=label + '?', relief=RIDGE, width=width)
    ent = Entry(row, relief=SUNKEN, textvariable=var)
    row.pack(fill=X)
    lab.pack(side=LEFT)
    ent.pack(side=LEFT, expand=YES, fill=X)
    if browse:
        btn = Button(row, text='browse...')
        btn.pack(side=RIGHT)
        if not extend:
            btn.config(command=lambda: var.set(askopenfilename() or var.get()))
        else:
            btn.config(command=lambda: var.set(var.get() + ' ' + askopenfilename()))
    return var
