"""
##############################################################################
a "mixin" class for other frames: common methods for canned dialogs,
spawning programs, simple text viewers, etc; this class must be mixed
with a Frame (or a subclass derived from Frame) for its quit method;
##############################################################################
"""
import sys
sys.path.append('C:\\Users\\10121976\\PycharmProjects')

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *

from PP4E.Gui.Tour.scrolledtext import ScrolledText
from PP4E.launchmodes import PortableLauncher, System


class GuiMixin:
    def infobox(self, title, text, *args):
        return showinfo(title, text)

    def errorbox(self, text):
        showerror('Error!', text)

    def question(self, title, text, *args):
        return askyesno(title, text)

    def notdone(self):
        showerror('Not implemented', 'Option not available')

    def quit(self):
        if self.question('Verify quit', 'Are you sure you want to quit?'):
            Frame.quit(self)

    def help(self):
        self.infobox('RTFM', 'See figure 1...')

    def selectOpenFile(self, file='', dir='.'):
        return askopenfilename(initialfile=file, initialdir=dir)

    def selectSaveFile(self, file='', dir='.'):
        return asksaveasfilename(initialfile=file, initialdir=dir)

    def clone(self, args=()):
        new = Toplevel()
        myclass = self.__class__
        myclass(new, *args)

    def spawn(self, pycmdline, wait=False):
        if not wait:
            PortableLauncher(pycmdline, pycmdline)()
        else:
            System(pycmdline, pycmdline)()

    def browser(self, filename):
        new = Toplevel()
        view = ScrolledText(new, file=filename)
        view.text.config(height=30, width=85)
        view.text.config(font=('courier', 10, 'normal'))
        new.title('Text Viewer')
        new.iconname('browser')


if __name__ == '__main__':
    class TestMixin(GuiMixin, Frame):  # standalone test
        def __init__(self, parent=None):
            Frame.__init__(self, parent)
            self.pack()
            Button(self, text='quit', command=self.quit).pack(fill=X)
            Button(self, text='help', command=self.help).pack(fill=X)
            Button(self, text='clone', command=self.clone).pack(fill=X)
            Button(self, text='spawn', command=self.other).pack(fill=X)

        def other(self):
            self.spawn('guimixin.py')

    TestMixin().mainloop()
