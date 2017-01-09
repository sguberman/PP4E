"""
##############################################################################
Classes that encapsulate top-level interfaces
Allows same GUI to be main, popup, or attached; content classes may inherit
from these directly, or be mixed together with them per usage mode; may also
be called directly without a subclass; designed to be mixed in after (further
to the right than) app-specific classes: else, subclass gets methods here
(destroy, okayToQuit), instead of from app-specific classes -- can't redefine.
##############################################################################
"""
import glob
import os
from tkinter import Tk, Toplevel, Frame, YES, BOTH, RIDGE
from tkinter.messagebox import showinfo, askyesno


class _window:
    """
    mixin shared by main and popup windows
    """
    foundicon = None
    iconpatt = '*.ico'
    iconmine = 'py.ico'

    def config_borders(self, app, kind, iconfile):
        if not iconfile:
            iconfile = self.find_icon()
        title = app
        if kind:
            title += ' - ' + kind
        self.title(title)
        self.iconname(app)
        if iconfile:
            try:
                self.iconbitmap(iconfile)
            except:
                pass
        self.protocol('WM_DELETE_WINDOW', self.quit)

    def find_icon(self):
        if _window.foundicon:
            return _window.foundicon
        iconfile = None
        iconshere = glob.glob(self.iconpatt)
        if iconshere:
            iconfile = iconshere[0]
        else:
            mymod = __import__(__name__)
            path = __name__.split('.')
            for mod in path[1:]:
                mymod = getattr(mymod, mod)
            mydir = os.path.dirname(mymod.__file__)
            myicon = os.path.join(mydir, self.iconmine)
            if os.path.exists(myicon):
                iconfile = myicon
        _window.foundicon = iconfile
        return iconfile


class MainWindow(Tk, _window):
    """
    when run in main toplevel window
    """
    def __init__(self, app, kind='', iconfile=None):
        Tk.__init__(self)
        self.__app = app
        self.config_borders(app, kind, iconfile)

    def quit(self):
        if self.okay_to_quit():
            if askyesno(self.__app, 'Verify Quit Program?'):
                self.destroy()
        else:
            showinfo(self.__app, 'Quit not allowed')

    def destroy(self):
        Tk.quit(self)

    def okay_to_quit(self):
        return True


class PopupWindow(Toplevel, _window):
    """
    when run ini secondary popup window
    """
    def __init__(self, app, kind='', iconfile=None):
        Toplevel.__init__(self)
        self.__app = app
        self.config_borders(app, kind, iconfile)

    def quit(self):
        if askyesno(self.__app, 'Verify Quit Window?'):
            self.destroy()

    def destroy(self):
        Toplevel.destroy(self)


class QuietPopupWindow(PopupWindow):
    def quit(self):
        self.destroy()


class ComponentWindow(Frame):
    """
    when attached to another display
    """
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.config(relief=RIDGE, border=2)

    def quit(self):
        showinfo('Quit', 'Not supported in attachment mode')
