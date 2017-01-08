"""
##############################################################################
An extended Frame that makes window menus and toolbars automatically.
Use GuiMakerFrameMenu for embedded components (makes frame-based menus).
Use GuiMakerWindowMenu for toplevel windows (makes Tk8.0 window menus).
See the self-test code for an example layout tree format.
##############################################################################
"""
import sys
from tkinter import *
from tkinter.messagebox import showinfo


class GuiMaker(Frame):
    menubar = []
    toolbar = []
    helpbutton = True

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.start()
        self.makeMenubar()
        self.makeToolbar()
        self.makeWidgets()

    def makeMenubar(self):
        """
        make menubar at the top (Tk8.0 menus below)
        expand=no, fill=x so same width on resize
        """
        menubar = Frame(self, relief=RAISED, bd=2)
        menubar.pack(side=TOP, fill=X)

        for (name, key, items) in self.menubar:
            mbutton = Menubutton(menubar, text=name, underline=key)
            mbutton.pack(side=LEFT)
            pulldown = Menu(mbutton)
            self.addMenuItems(pulldown, items)
            mbutton.config(menu=pulldown)

        if self.helpbutton:
            Button(menubar, text='Help',
                            cursor='gumby',
                            relief=FLAT,
                            command=self.help).pack(side=RIGHT)

    def addMenuItems(self, menu, items):
        for item in items:
            if item == 'separator':
                menu.add_separator({})
            elif type(item) == list:
                for num in item:
                    menu.entryconfig(num, state=DISABLED)
            elif type(item[2]) != list:
                menu.add_command(label=item[0],
                                 underline=item[1],
                                 command=item[2])
            else:
                pullover = Menu(menu)
                self.addMenuItems(pullover, item[2])
                menu.add_cascade(label=item[0],
                                 underline=item[1],
                                 menu=pullover)

    def makeToolbar(self):
        """
        make button bar at bottom, if any
        expand=no, fill=x so same width on resize
        this could support images too, would need prebuilt
        gifs or PIL for thumbnails
        """
        if self.toolbar:
            toolbar = Frame(self, cursor='hand2', relief=SUNKEN, bd=2)
            toolbar.pack(side=BOTTOM, fill=X)
            for (name, action, where) in self.toolbar:
                Button(toolbar, text=name, command=action).pack(where)

    def makeWidgets(self):
        """
        make 'middle' part last, so menu/toolbar
        is always  on top/bottom and clipped last;
        override this default, pack middle any side;
        for grid: grid middle part in a packed frame
        """
        name = Label(self,
                     width=40, height=10,
                     relief=SUNKEN, bg='white',
                     text=self.__class__.__name__,
                     cursor='crosshair')
        name.pack(expand=YES, fill=BOTH, side=TOP)

    def help(self):
        """override me in subclass"""
        showinfo('Help', 'Sorry, no help for ' + self.__class__.__name__)

    def start(self):
        """override me in subclass: set menu/toolbar with self"""
        pass


##############################################################################
# Customize for Tk 8.0 main window menu bar, instead of a frame
##############################################################################

GuiMakerFrameMenu = GuiMaker  # use this for embedded component menus


class GuiMakerWindowMenu(GuiMaker):  # use this for toplevel window menus
    def makeMenubar(self):
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        for (name, key, items) in self.menubar:
            pulldown = Menu(menubar)
            self.addMenuItems(pulldown, items)
            menubar.add_cascade(label=name, underline=key, menu=pulldown)

        if self.helpbutton:
            if sys.platform[:3] == 'win':
                menubar.add_command(label='Help', command=self.help)
            else:
                pulldown = Menu(menubar)  # Linux needs real pulldown
                pulldown.add_command(label='About', command=self.help)
                menubar.add_cascade(label='Help', menu=pulldown)


##############################################################################
# Self-test when file run standalone: `python guimaker.py`
##############################################################################

if __name__ == '__main__':
    from guimixin import GuiMixin

    menubar = [
        ('File', 0,
            [('Open', 0, lambda: 0),
             ('Quit', 0, sys.exit)]),
        ('Edit', 0,
            [('Cut', 0, lambda: 0),
             ('Paste', 0, lambda: 0)])
    ]

    toolbar = [('Quit', sys.exit, {'side': LEFT})]


    class TestAppFrameMenu(GuiMixin, GuiMakerFrameMenu):
        def start(self):
            self.menubar = menubar
            self.toolbar = toolbar


    class TestAppWindowMenu(GuiMixin, GuiMakerWindowMenu):
        def start(self):
            self.menubar = menubar
            self.toolbar = toolbar


    class TestAppWindowMenuBasic(GuiMakerWindowMenu):
        def start(self):
            self.menubar = menubar
            self.toolbar = toolbar  # guimaker help, not guimixin


    root = Tk()
    TestAppFrameMenu(Toplevel())
    TestAppWindowMenu(Toplevel())
    TestAppWindowMenuBasic(root)
    root.mainloop()
