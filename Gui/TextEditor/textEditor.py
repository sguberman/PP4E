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

from ..Tools.guimaker import *


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
        from .textConfig import (
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
        name = Label(self, bg='black', fg='white')
        name.pack(side=TOP, fill=X)

        vbar = Scrollbar(self)
        hbar = Scrollbar(self, orient='horizontal')
        text = Text(self, padx=5, wrap='none')
        text.config(undo=1, autoseparators=1)

        vbar.pack(side=RIGHT, fill=Y)
        hbar.pack(side=BOTTOM, fill=X)
        text.pack(side=TOP, fill=BOTH, expand=YES)

        text.config(yscrollcommand=vbar.set)
        text.config(xscrollcommand=hbar.set)
        vbar.config(command=text.yview)
        hbar.config(command=text.xview)

        # 2.0: apply user configs or defaults
        startfont = configs.get('font', self.fonts[0])
        startbg = configs.get('bg', self.colors[0]['bg'])
        startfg = configs.get('fg', self.colors[0]['fg'])
        text.config(font=startfont, bg=startbg, fg=startfg)
        if 'height' in configs:
            text.config(height=configs['height'])
        if 'width' in configs:
            text.config(width=configs['width'])
        self.text = text
        self.filelabel = name

    ##########################################################################
    # File menu commands
    ##########################################################################

    def my_askopenfilename(self):
        if not self.openDialog:
            self.openDialog = Open(initialdir=self.startfiledir,
                                   filetypes=self.ftypes)
        return self.openDialog.show()

    def my_asksaveasfilename(self):
        if not self.saveDialog:
            self.saveDialog = SaveAs(initialdir=self.startfiledir,
                                     filetypes=self.ftypes)
        return self.saveDialog.show()

    def onOpen(self, loadFirst='', loadEncode=''):
        """
        2.1: total rewrite for Unicode support; open in text mode with an
        encoding passed in, input from the user, in textconfig, or platform
        default, or open as binary bytes for arbitrary Unicode encodings as
        last resor and drop \r iin Windows end-lines if present so text
        displays normally; content fetches are returned as str, so need to
        encode on saves: keep encoding used here;

        tests if file is okay ahead of time to try to avoid opens; we could
        also load and manually decode bytes to str to avoid multiple open
        attempts, but this is unlikely to try all cases;

        encoding behavior is configurable in the local textConfig.py:
        1) try known type first if passed in by client (email charsets)
        2) if opensAskUser True, try user input next (prefill with defaults)
        3) if opensEncoding nonempty, try this encoding next
        4) try sys.getdefaultencoding() platform default
        5) finally try binary mode bytes and Tk policy as last resort
        """
        if self.text_edit_modified():
            if not askyesno('PyEdit', 'Text has changed: discard changes?'):
                return
        file = loadFirst or self.my_askopenfilename()

        if not file:
            return

        if not os.path.isfile(file):
            showerror('PyEdit', 'Could not open file ' + file)
            return

        # try known encoding if passed and accurate (eg, email)
        text = None
        if loadEncode:
            try:
                text = open(file, 'r', encoding=loadEncode).read()
                self.knownEncoding = loadEncode
            except (UnicodeError, LookupError, IOError):
                pass

        # try user input, prefill with next choice as default
        if text is None and self.opensAskUser:
            self.update()  # else dialog doesn't appear in rare cases
            askuser = askstring('PyEdit', 'Enter Unicode encoding for open',
                                initialvalue=(self.opensEncoding or
                                              sys.getdefaultencoding() or ''))
            self.text.focus()
            if askuser:
                try:
                    text = open(file, 'r', encoding=askuser).read()
                    self.knownEncoding = askuser
                except (UnicodeError, LookupError, IOError):
                    pass

        # try config file
        if text is None and self.opensEncoding:
            try:
                text = open(file, 'r', encoding=self.opensEncoding).read()
                self.knownEncoding = self.opensEncoding
            except (UnicodeError, LookupError, IOError):
                pass

        # try platform default
        if text is None:
            try:
                text = open(file, 'r', encoding=sys.getdefaultencoding()).read()
                self.knownEncoding = sys.getdefaultencoding()
            except (UnicodeError, LookupError, IOError):
                pass

        # last resort: use binary bytes and rely on Tk to decode
        if text is None:
            try:
                text = open(file, 'rb').read()
                text = text.replace(b'\r\n', b'\n')
                self.knownEncoding = None
            except IOError:
                pass

        if text is None:
            showerror('PyEdit', 'Could not decode and open file ' + file)
        else:
            self.setAllText(text)
            self.setFileName(file)
            self.text.edit_reset()  # 2.0: clear undo/redo stacks
            self.text.edit_modified(0)  # 2.0: clear modified flag

    def onSave(self):
        self.onSaveAs(self.currfile)

    def onSaveAs(self, forcefile=None):
        """
        2.1: total rewrite for Unicord support: Text content is always
        returned as str, so we must deal with encodings to save to a file
        here, regardless of open mode of the output file (binary requires
        bytes, and text must encode); tries the encoding used when opened or
        saved (if known), user input, config file setting, and platform
        default last; most users can use platform default;

        retains successful encoding name here for next save, because this may
        be the first Save after New or a manual text insertion; Save and
        SaveAs may both be used for Save, but SaveAs usage is unclear); gui
        prompts are prefilled with the known encoding if there is one;

        does manual text.encode() to avoid creating file; text mode files
        perform platform specific endline conversion: Windows \r dropped if
        present on open by text mode (auto) and binary mode (manually); if
        manual content inserts, must delete \r else duplicates here;
        knownEncoding=None before first Open or Save, after New, if binary
        Open;

        encoding behavior is configurable in the local textConfig.py:
        1) if savesUseKnownEncoding > 0, try encoding from last open or save
        2) if savesAskUser True, try user input next
        3) if savesEncoding nonempty, try this encoding next
        4) tries sys.getdefaultencoding() as a last resort
        """
        filename = forcefile or self.my_asksaveasfilename()
        if not filename:
            return

        text = self.getAllText()
        encpick = None

        # try known encoding at latest Open or Save, if any
        if self.knownEncoding and ((
            forcefile and self.savesUseKnownEncoding >= 1) or (
            not forcefile and self.savesUseKnownEncoding >= 2)):
            try:
                text.encode(self.knownEncoding)
                encpick = self.knownEncoding
            except UnicodeError:
                pass

        # try user input, prefill with known type, else next choice
        if not encpick and self.savesAskUser:
            self.update()
            askuser = askstring('PyEdit', 'Enter Unicode encoding for save',
                                initialvalue=(self.knownEncoding or
                                              self.savesEncoding or
                                              sys.getdefaultencoding() or ''))
            self.text.focus()
            if askuser:
                try:
                    text.encode(askuser)
                    encpick = askuser
                except (UnicodeError, LookupError):
                    pass

        # try config file
        if not encpick and self.savesEncoding:
            try:
                text.encode(self.savesEncoding)
                encpick = self.savesEncoding
            except (UnicodeError, LookupError):
                pass

        # try platform default
        if not encpick:
            try:
                text.encode(sys.getdefaultencoding())
                encpick = sys.getdefaultencoding()
            except (UnicodeError, LookupError):
                pass

        # open in text mode fo endlines + encoding
        if not encpick:
            showerror('PyEdit', 'Could not encode for file ' + filename)
        else:
            try:
                file = open(filename, 'w', encoding=encpick)
                file.write(text)
                file.close()
            except:
                showerror('PyEdit', 'Could not write file ' + filename)
            else:
                self.setFileName(filename)
                self.text.edit_modified(0)
                self.knownEncoding = encpick

    def onNew(self):
        """
        start editing a new file from scratch in current window;
        see onClone to popup a new independent edit window instead;
        """
        if self.text_edit_modified():
            if not askyesno('PyEdit', 'Text has changed: discard changes?'):
                return
        self.setFileName(None)
        self.clearAllText()
        self.text.edit_reset()
        self.text.edit_modified(0)
        self.knownEncoding = None

    def onQuit(self):
        """
        on Quit menu/toolbar select and wm border X button in toplevel windows;
        2.1: don't exit app if others changed; 2.0: don't ask if self unchanged;
        moved to the toplevel window classes at the end since may vary per
        usage: a Quit in GUI might quit() to exit, destroy() just one Toplevel,
        Tk, or edit frame, or not be provided at all when run as an attached
        component; check self for changes, and if might quit(), main windows
        should check other windows in the process-wide list to see if they have
        changed too;
        """
        assert False, 'onQuit must be defined in window-specific subclass'

    def text_edit_modified(self):
        """
        2.1: this now works! seems to have been a bool result type issue in
        tkinter; 2.0: self.text.edit_modified() broken in Python 2.4: do
        manually for now;
        """
        return self.text.edit_modified()
        #return self.tk.call((self.text._w, 'edit') + ('modified', None))

    ##########################################################################
    # Edit menu commands
    ##########################################################################

    def onUndo(self):
        try:
            self.text.edit_undo()
        except TclError:
            showinfo('PyEdit', 'Nothing to undo')

    def onRedo(self):
        try:
            self.text.edit_redo()
        except TclError:
            showinfo('PyEdit', 'Nothing to redo')

    def onCopy(self):
        if not self.text.tag_ranges(SEL):
            showerror('PyEdit', 'No text selected')
        else:
            text = self.text.get(SEL_FIRST, SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)

    def onDelete(self):
        if not self.text.tag_ranges(SEL):
            showerror('PyEdit', 'No text selected')
        else:
            self.text.delete(SEL_FIRST, SEL_LAST)

    def onCut(self):
        if not self.text.tag_ranges(SEL):
            showerror('PyEdit', 'No text selected')
        else:
            self.onCopy()
            self.onDelete()

    def onPaste(self):
        try:
            text = self.selection_get(selection='CLIPBOARD')
        except TclError:
            showerror('PyEdit', 'Nothing to paste')
            return
        self.text.insert(INSERT, text)
        self.text.tag_remove(SEL, '1.0', END)
        self.text.tag_add(SEL, INSERT+'-%dc' % len(text), INSERT)
        self.text.see(INSERT)

    def onSelectALL(self):
        self.text.tag_add(SEL, '1.0', END+'-1c')
        self.text.mark_set(INSERT, '1.0')
        self.text.see(INSERT)

    ##########################################################################
    # Search menu commands
    ##########################################################################

    def onGoto(self, forceline=None):
        line = forceline or askinteger('PyEdit', 'Enter line number')
        self.text.update()
        self.text.focus()
        if line is not None:
            maxindex = self.text.index(END+'-1c')
            maxline = int(maxindex.split('.')[0])
            if 0 < line <= maxline:
                self.text.mark_set(INSERT, '%d.0' % line)
                self.text.tag_remove(SEL, '1.0', END)
                self.text.tag_add(SEL, INSERT, 'insert + 1l')
                self.text.see(INSERT)
            else:
                showerror('PyEdit', 'Bad line number')

    def onFind(self, lastkey=None):
        key = lastkey or askstring('PyEdit', 'Enter search string')
        self.text.update()
        self.text.focus()
        self.lastfind = key
        if key:
            nocase = configs.get('caseinsens', True)
            where = self.text.search(key, INSERT, END, nocase=nocase)
            if not where:
                showerror('PyEdit', 'String not found')
            else:
                pastkey = where + '+%dc' %len(key)
                self.text.tag_remove(SEL, '1.0', END)
                self.text.tag_add(SEL, where, pastkey)
                self.text.mark_set(INSERT, pastkey)
                self.text.see(where)

    def onRefind(self):
        self.onFind(self.lastfind)

    def onChange(self):
        """
        non-modal find/change dialog
        2.1: pass per-dialog inputs to callbacks, may be > 1 change dialog open
        """
        new = Toplevel(self)
        new.title('PyEdit - change')
        Label(new, text='Find text?', relief=RIDGE, width=15).grid(row=0,
                                                                   column=0)
        Label(new, text='Change to?', relief=RIDGE, width=15).grid(row=1,
                                                                   column=0)
        entry1 = Entry(new)
        entry2 = Entry(new)
        entry1.grid(row=0, column=1, sticky=EW)
        entry2.grid(row=1, column=1, sticky=EW)

        def onFind():
            self.onFind(entry1.get())

        def onApply():
            self.onDoChange(entry1.get(), entry2.get())

        Button(new, text='Find', command=onFind).grid(row=0, column=2,
                                                      sticky=EW)
        Button(new, text='Apply', command=onApply).grid(row=1, column=2,
                                                        sticky=EW)
        new.columnconfigure(1, weight=1)

    def onDoChange(self, findtext, changeto):
        # on Apply in change dialog: change and refind
        if self.text.tag_ranges(SEL):
            self.text.delete(SEL_FIRST, SEL_LAST)
            self.text.insert(INSERT, changeto)
            self.text.see(INSERT)
            self.onFind(findtext)
            self.text.update()

    def onGrep(self):
        """
        new in version 2.1: threaded external file search;
        search matched filenames in directory tree for string;
        listbox clicks open matched file at line of occurrene;

        search is threaded so the GUI remains active and is not
        blocked, and to allow multiple greps to overlap in time;
        could use threadtools, but avoid loop in no active grep;

        grep Unicode policy: text files content in the searched tree
        might be in any Unicode encoding: we don't ask about each (as
        we do for opens), but allow the encoding used for the entire
        tree to be input, preset it to the platform filesystem or text
        default, and skip files that fail to decode; in worst cases, users
        may need to run grep N times if N encodings might exist; else opens
        may raise exceptions, and opening in binary mode might fail to match
        encoded text against search string;

        TBD: better to issue an error if any file fails to decode? but utf-16
        2-bytes/char format created in Notepad may decode without error per
        utf-8, and search strings won't be found;
        TBD: could allow input of multiple encoding names, split on comma, try
        each one for every file, without open loadEncode?
        """
        from ..ShellGui.formrows import makeFormRow

        # nonmodal dialog: get dirname, filenamepatt, grepkey
        popup = Toplevel()
        popup.title('PyEdit - grep')
        var1 = makeFormRow(popup, label='Directory root',
                           width=18, browse=False)
        var2 = makeFormRow(popup, label='Filename pattern',
                           width=18, browse=False)
        var3 = makeFormRow(popup, label='Search string',
                           width=18, browse=False)
        var4 = makeFormRow(popup, label='Content encoding',
                           width=18, browse=False)
        var1.set('.')
        var2.set('*.py')
        var4.set(sys.getdefaultencoding())
        cb = lambda: self.onDoGrep(var1.get(), var2.get(),
                                   var3.get(), var4.get())
        Button(popup, text='Go', command=cb).pack()

    def onDoGrep(self, dirname, filenamepatt, grepkey, encoding):
        """
        on Go in grep dialog: populate scrolled list with matches
        tbd: should producer thread be daemon so it dies with app?
        """
        import threading, queue

        # make nonmodal uncloseable dialog
        mypopup = Tk()
        mypopup.title('PyEdit - grepping')
        status = Label(mypopup, text='Grep thread searching for: %r...'
                       % grepkey)
        status.pack(padx=20, pady=20)
        mypopup.protocol('WM_DELETE_WINDOW', lambda: None)  # ignore X close

        # start producer thread, consumer loop
        myqueue = queue.Queue()
        threadargs = (filenamepatt, dirname, grepkey, encoding, myqueue)
        threading.Thread(target=self.grepThreadProducer,
                         args=threadargs).start()
        self.grepThreadConsumer(grepkey, encoding, myqueue, mypopup)

    def grepThreadProducer(self, filenamepatt, dirname, grepkey,
                           encoding, myqueue):
        """
        in a non-GUI parallel thread: queue find.find results list;
        could also queue matches as found, but need to keep window;
        file content and file names may both fail to decode here;

        TBD: could pass encoded bytes to find() to avoid filename decoding
        excs in os.walk/listdir, but which encoding to use:
        sys.getfilesystemencoding() if not None? see also Chapter 6
        footnote issue: 3.1 fnmatch always converts bytes per Latin-1;
        """
        from ...Tools.find import find

        matches = []
        try:
            for filepath in find(pattern=filenamepatt, startdir=dirname):
                try:
                    textfile = open(filepath, encoding=encoding)
                    for (linenum, linestr) in enumerate(textfile):
                        if grepkey in linestr:
                            msg = '%s@%d [%s]' % (filepath, linenum + 1,
                                                  linestr)
                            matches.append(msg)
                except UnicodeError as X:
                    print('Unicode error in:', filepath, X)
                except IOError as X:
                    print('IO error in:', filepath, X)
        finally:
            myqueue.put(matches)

    def grepThreadConsumer(self, grepkey, encoding, myqueue, mypopup):
        pass
