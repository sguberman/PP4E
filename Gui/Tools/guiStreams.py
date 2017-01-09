"""
##############################################################################
first-cut implementation of file-like classes that can be used to redirect
input and output streams to GUI displays; as is, input comes from a common
dialog popup (a single output+input interface or a persistent Entry field
for input would be better); this also does not properly span lines for read
requests with a byte count > len(line); could also add __iter__/__next__ to
GuiInput to support line iteration like files but would be too many popups;
##############################################################################
"""
from tkinter import *
from tkinter.simpledialog import askstring
from tkinter.scrolledtext import ScrolledText


class GuiOutput:
    font = ('courier', 9, 'normal')

    def __init__(self, parent=None):
        self.text = None
        if parent:
            self.popupnow(parent)

    def popupnow(self, parent=None):
        if self.text:
            return
        self.text = ScrolledText(parent or Toplevel())
        self.text.config(font=self.font)
        self.text.pack()

    def write(self, text):
        self.popupnow()
        self.text.insert(END, str(text))
        self.text.see(END)
        self.text.update()

    def writelines(self, lines):
        for line in lines:
            self.write(line)


class GuiInput:
    def __init__(self):
        self.buff = ''

    def inputline(self):
        line = askstring('GuiInput', 'Enter input line + <crlf> (cancel=eof)')
        if line is None:
            return ''
        else:
            return line + '\n'

    def read(self, bytes=None):
        if not self.buff:
            self.buff = self.inputline()
        if bytes:
            text = self.buff[:bytes]
            self.buff = self.buff[bytes:]
        else:
            text = ''
            line = self.buff
            while line:
                text = text + line
                line = self.inputline()
        return text

    def readline(self):
        text = self.buff or self.inputline()
        self.buff = ''
        return text

    def readlines(self):
        lines = []
        while True:
            next = self.readline()
            if not next:
                break
            lines.append(next)
        return lines


def redirectedGuiFunc(func, *args, **kwargs):
    import sys
    savestreams = sys.stdin, sys.stdout
    sys.stdin = GuiInput()
    sys.stdout = GuiOutput()
    sys.stderr = sys.stdout
    result = func(*args, **kwargs)
    sys.stdin, sys.stdout = savestreams
    return result


def redirectedGuiShellCmd(command):
    import os
    input = os.popen(command, 'r')
    output = GuiOutput()

    def reader(input, output):
        while True:
            line = input.readline()
            if not line:
                break
            output.write(line)

    reader(input, output)


if __name__ == '__main__':
    def makeUpper():
        while True:
            try:
                line = input('Line? ')
            except:
                break
            print(line.upper())
        print('end of file')

    def makeLower(input, output):
        while True:
            line = input.readline()
            if not line:
                break
            output.write(line.lower())
        print('end of file')

    root = Tk()
    Button(root, text='test streams', command=lambda: redirectedGuiFunc(makeUpper)).pack(fill=X)
    Button(root, text='test files', command=lambda: makeLower(GuiInput(), GuiOutput())).pack(fill=X)
    Button(root, text='test popen', command=lambda: redirectedGuiShellCmd('dir *')).pack(fill=X)
    root.mainloop()
