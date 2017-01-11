"""
read command pipe in a thread and place output on a queue checked in timer loop;
allows script to display program's output without being blocked between its outputs;
spawned programs need not connect or flush, but this approaches complexity of sockets
"""
import _thread as thread
import queue
import os
from tkinter import Tk

from PP4E.Gui.Tools.guiStreams import GuiOutput


stdoutqueue = queue.Queue()


def producer(input):
    while True:
        line = input.readline()
        stdoutqueue.put(line)
        if not line:
            break


def consumer(output, root, term='<end>'):
    try:
        line = stdoutqueue.get(block=False)
    except queue.Empty:
        pass
    else:
        if not line:
            output.write(term)
            return
        output.write(line)
    root.after(250, lambda: consumer(output, root, term))


def redirectedGuiShellCmd(command, root):
    input = os.popen(command, 'r')
    output = GuiOutput(root)
    thread.start_new_thread(producer, (input,))
    consumer(output, root)


if __name__ == '__main__':
    win = Tk()
    redirectedGuiShellCmd('python -u pipe-nongui.py', win)
    win.mainloop()
