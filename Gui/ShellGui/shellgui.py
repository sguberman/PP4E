"""
##############################################################################
tools launcher; uses guimaker templates, guimixn std quit dialog;
I am just a class library: run mytools script to display the GUI;
##############################################################################
"""
from tkinter import *

from PP4E.Gui.Tools.guimixin import GuiMixin
from PP4E.Gui.Tools.guimaker import *


class ShellGui(GuiMixin, GuiMakerWindowMenu):
    def start(self):
        self.setMenubar()
        self.setToolbar()
        self.master.title('Shell Tools Listbox')
        self.master.iconname('Shell Tools')

    def handle_list(self, event):
        label = self.listbox.get(ACTIVE)
        self.run_command(label)

    def makeWidgets(self):
        sbar = Scrollbar(self)
        list = Listbox(self, bg='white')
        sbar.config(command=list.yview)
        list.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        list.pack(side=LEFT, expand=YES, fill=BOTH)
        for (label, action) in self.fetch_commands():
            list.insert(END, label)
        list.bind('<Double-1>', self.handle_list)
        self.listbox = list

    def forToolbar(self, label):
        return True

    def setToolbar(self):
        self.toolbar = []
        for (label, action) in self.fetch_commands():
            if self.forToolbar(label):
                self.toolbar.append((label, action, dict(side=LEFT)))
        self.toolbar.append(('Quit', self.quit, dict(side=RIGHT)))

    def setMenubar(self):
        tool_entries = []
        self.menubar = [
            ('File', 0, [('Quit', -1, self.quit)]),
            ('Tools', 0, tool_entries)
        ]
        for (label, action) in self.fetch_commands():
            tool_entries.append((label, -1, action))


##############################################################################
# delegate to template type-specific subclasses
# which delegate to ap tool-set-specific subclasses
##############################################################################


class ListMenuGui(ShellGui):
    def fetch_commands(self):
        return self.myMenu

    def run_command(self, cmd):
        for (label, action) in self.myMenu:
            if label == cmd:
                action()


class DictMenuGui(ShellGui):
    def fetch_commands(self):
        return self.myMenu.items()

    def run_command(self, cmd):
        self.myMenu[cmd]()
