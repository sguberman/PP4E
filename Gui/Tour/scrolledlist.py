from tkinter import *

class ScrolledList(Frame):
    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.make_widgets(options)

    def handle_list(self, event):
        index = self.listbox.curselection()
        label = self.listbox.get(index)
        self.run_command(label)

    def make_widgets(self, options):
        sbar = Scrollbar(self)
        list = Listbox(self, relief=SUNKEN)
        sbar.config(command=list.yview)
        list.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        list.pack(side=LEFT, expand=YES, fill=BOTH)
        pos = 0
        for label in options:
            list.insert(pos, label)
            pos += 1
        #list.config(selectmode=SINGLE, setgrid=1)
        list.bind('<Double-1>', self.handle_list)
        self.listbox = list

    def run_command(self, selection):
        print('You selected:', selection)


if __name__ == '__main__':
    options = (('Lumberjack-%s' % x) for x in range(20))
    ScrolledList(options).mainloop()
