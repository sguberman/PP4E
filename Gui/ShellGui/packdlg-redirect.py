# wrap commandline script iin GUI redirection tool to popup its output

from tkinter import *

from packdlg import runPackDialog
from PP4E.Gui.Tools.guiStreams import redirectedGuiFunc


def runPackDialog_Wrapped():
    redirectedGuiFunc(runPackDialog)


if __name__ == '__main__':
    root = Tk()
    Button(root, text='popup', command=runPackDialog_Wrapped).pack(fill=X)
    root.mainloop()
