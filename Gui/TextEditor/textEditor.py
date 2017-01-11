"""
##############################################################################
PyEdit 2.1: a Python/tkinter text file editor and component.

Uses the Tk text widget, plus GuiMaker menus and toolbar buttons to
implement a full-featured text editor that can be run as a standalone
program and attached as a component to other GUIs. Also used by
PyMailGUI and PyView to edit mail text and image file notes, and by
PyDemos in popup mode to display source and text files.

New in version 2.1 (4E)
-updated to run under Python 3.X (3.1)
-added "grep" search menu option and dialog: threaded external files search
-verify app exit on quit if changes in other edit windows in process
-supports arbitrary Unicode encodings for files: per textConfig.py settings
-update change and font dialog implementations to allow many to be open
-runs self.update() before setting text in new editor for loadFirst
-various improvements to the Run Code option, per the next section

2.1 Run Code improvements:
-use base name after chdir to run code file, not possibly relative path
-use launch modes that support arguments for run code file mode on Windows
-run code inherits launchmodes backslash conversion (no longer required)

New in version 2.0 (3E)
-added simple font components input dialog
-use Tk 8.4 undo stack API to add undo/redo text modifications
-now verifies on quit, open, new, run, only if text modified and unsaved
-searches are case-insensitive now by default
-configuration module for initial font/color/size/searchcase

TBD (and suggested exercises):
-could also allow search case choice in GUI (not just config file)
-could use re patterns for searches and greps (see text chapter)
-could experiment with syntax-directed text colorization (see IDLE, others)
-could try to verify app exit for quit() in non-managed windows too
-could queue each result as found in grep dialog thread to avoid delay
-could use images in toolbar buttons (per examples of this in Chapter 9)
-could scan line to map Tk insert position column to account for tabs on Info
-could experiment with "grep" tbd Unicode issues (see notes in the code);
##############################################################################
"""

Version = '2.1'
import os
import sys
from tkinter import *
from tkinter.filedialog import Open, SaveAs
from tkinter.messagebox import showinfo, showerror, askyesno
from tkinter.simpledialog import askstring, askinteger
from tkinter.colorchooser import askcolor

from PP4E.Gui.Tools.guimaker import *


# general configurations
try:
    import textConfig
    configs = textConfig.__dict__
except:
    configs = {}

helptext = """PyEdit version %s
April, 2010
(2.0: January, 2006)
(1.0: October, 2000)

Programming Python, 4th Edition
Mark Lutz, for O'Reilly Media, Inc.

A text editor program and embeddable object
component, written in Python/tkinter. Use
menu tear-offs and toolbar for quick access
to actions, and Alt-key shortcuts for menus.

Additions in version %s:
- supports Python 3.X
- new "grep" external files search dialog
- verifies app quit if other edit windows changed
- supports arbitrary Unicode encodings for files
- allows multiple change and font dialogs
- various improvements to the Run Code option

Prior version additions:
- font pick dialog
- unlimited undo/redo
- quit/open/new/run prompt save only if changed
- searches are case-insensitive
- startup configuration module textConfig.py
"""

START = '1.0'  # index of first char: row=1, col=0
SEL_FIRST = SEL + '.first'  # map sel tag to index
SEL_LAST = SEL + '.last'  # same as 'sel.last'

FontScale = 0  # use bigger font on Linux
if sys.platform[:3] != 'win':
    FontScale = 3


##############################################################################
# Main class: implements editor GUI, actions
# requires a flavor of GuiMaker to be mixed in by more specific subclasses;
# not a direct subclass of GuiMaker because that class takes multiple forms.
##############################################################################

class TextEditor:  # mix with menu/toolbar Frame class
    startfiledir = '.'  # for dialogs
    editwindows = []  # for process-wide quit check

    # Unicode configurations
    # imported in class to allow overrides in subclass or self
    if __name__ == '__main__':
        from textConfig import (
            opensAskUser, opensEncoding, savesUseKnownEncoding, savesAskUser,
            savesEncoding)
    else:
        from .textConfig import (
            opensAskUser, opensEncoding, savesUseKnownEncoding, savesAskUser,
            savesEncoding)

    ftypes = [('All files', '*'),  # for file open dialog
              ('Text files', '.txt'),
              ('Python files', '.py')]

    colors = [{'fg': 'black', 'bg': 'white'},  # color pick list
              {'fg': 'yellow', 'bg': 'black'},
              {'fg': 'white', 'bg': 'blue'},
              {'fg': 'black', 'bg': 'beige'},
              {'fg': 'yellow', 'bg': 'purple'},
              {'fg': 'black', 'bg': 'brown'},
              {'fg': 'lightgreen', 'bg': 'darkgreen'},
              {'fg': 'darkblue', 'bg': 'orange'},
              {'fg': 'orange', 'bg': 'darkblue'}]

    fonts = [('courier', 9+FontScale, 'normal'),  # platform-neutral fonts
             ('courier', 12+FontScale, 'normal'),
             ('courier', 10+FontScale, 'bold'),
             ('courier', 10+FontScale, 'italic'),
             ('times', 10+FontScale, 'normal'),
             ('helvetica', 10+FontScale, 'normal'),
             ('ariel', 10+FontScale, 'normal'),
             ('system', 10+FontScale, 'normal'),
             ('courier', 20+FontScale, 'normal')]

    def __init__(self, loadFirst='', loadEncode=''):
        if not isinstance(self, GuiMaker):
            raise TypeError('TextEditor needs a GuiMaker mixin')
        self.setFileName(None)
        self.lastfind = None
        self.openDialog = None
        self.saveDialog = None
        self.knownEncoding = None
        self.text.focus()
        if loadFirst:
            self.update()
            self.onOpen(loadFirst, loadEncode)

    def start(self):  # run by GuiMaker.__init__
        self.menuBar = [
            ('File', 0,
                [('Open...', 0, self.onOpen),
                 ('Save', 0, self.onSave),
                 ('Save As...', 5, self.onSaveAs),
                 ('New', 0, self.onNew),
                 'separator',
                 ('Quit', 0, self.onQuit)]
             ),
            ('Edit', 0,
                [('Undo', 0, self.onUndo),
                 ('Redo', 0, self.onRedo),
                 'separator',
                 ('Cut', 0, self.onCut),
                 ('Copy', 1, self.onCopy),
                 ('Paste', 0, self.onPaste),
                 'separator',
                 ('Delete', 0, self.onDelete),
                 ('Select All', 0, self.onSelectAll)]
             ),
            ('Search', 0,
                [('Goto...', 0, self.onGoto),
                 ('Find...', 0, self.onFind),
                 ('Refind', 0, self.onRefind),
                 ('Change...', 0, self.onChange),
                 ('Grep', 3, self.onGrep)]
             ),
            ('Tools', 0,
                [('Pick Font...', 6, self.onPickFont),
                 ('Font List', 0, self.onFontList),
                 'separator',
                 ('Pick Bg...', 3, self.onPickBg),
                 ('Pick Fg...', 0, self.onPickFg),
                 ('Color List', 0, self.onColorList),
                 'separator',
                 ('Info...', 0, self.onInfo),
                 ('Clone', 1, self.onClone),
                 ('Run Code', 0, self.onRunCode)]
             )
        ]

        self.toolBar = [
            ('Save', self.onSave, {'side': LEFT}),
            ('Cut', self.onCut, {'side': LEFT}),
            ('Copy', self.onCopy, {'side': LEFT}),
            ('Paste', self.onPaste, {'side': LEFT}),
            ('Find', self.onFind, {'side': LEFT}),
            ('Help', self.help, {'side': RIGHT}),
            ('Quit', self.onQuit, {'side': RIGHT})
        ]

    def makeWidgets(self):  # run by GuiMaker.__init__
        pass
