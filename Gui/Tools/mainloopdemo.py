"""
##############################################################################
demo running two distinct mainloop calls; each returns after the main window
is closed; save user results on Python object: GUI is gone; GUIs normally
configure widgets and then run just one mainloop, and have all their logic
in callbacks; this demo uses mainloop calls to implement two modal user
interactions from a non-GUI main program; it shows one way to add a GUI
component to an existing no-GUI script, without restructuring code;
##############################################################################
"""
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename


class Demo(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack()
        Label(self, text='Basic demos').pack()
        Button(self, text='open', command=self.openfile).pack(fill=BOTH)
        Button(self, text='save', command=self.savefile).pack(fill=BOTH)
        self.open_name = self.save_name = ''

    def openfile(self):
        self.open_name = askopenfilename(initialdir='.')

    def savefile(self):
        self.save_name = asksaveasfilename(initialdir='.')


if __name__ == '__main__':
    # display window once
    print('popup1...')
    mydialog = Demo()
    mydialog.mainloop()
    print(mydialog.open_name)
    print(mydialog.save_name)
    # Non GUI section of program uses mydialog here

    # display window again
    print('popup2...')
    mydialog = Demo()
    mydialog.mainloop()
    print(mydialog.open_name)
    print(mydialog.save_name)
    # Non GUI section of program uses mydialog again

    print('ending...')
