from tkinter import *


class Alarm(Frame):
    def __init__(self, msecs=1000):
        Frame.__init__(self)
        self.msecs = msecs
        self.pack()
        stopper = Button(self, text='Stop the beeps!', command=self.quit)
        stopper.pack()
        stopper.config(bg='navy', fg='white', bd=8)
        self.stopper = stopper
        self.repeater()

    def repeater(self):
        self.bell()
        self.stopper.flash()
        self.after(self.msecs, self.repeater)


if __name__ == '__main__':
    Alarm(msecs=1000).mainloop()
