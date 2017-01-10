# GUI that displays data produced and queued by worker threads (class-based)

import threading, queue, time
from tkinter.scrolledtext import ScrolledText


class ThreadGui(ScrolledText):
    threads_per_click = 4

    def __init__(self, parent=None):
        ScrolledText.__init__(self, parent)
        self.pack()
        self.dataqueue = queue.Queue()  # infinite size
        self.bind('<Button-1>', self.makethreads)  # on left mouse click
        self.consumer()  # queue loop in main thread

    def producer(self, id):
        for i in range(5):
            time.sleep(0.1)
            self.dataqueue.put('[producer id=%d, count=%d]' % (id, i))

    def consumer(self):
        try:
            data = self.dataqueue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.insert('end', 'consumer got => %s\n' % str(data))
            self.see('end')
        self.after(100, self.consumer)

    def makethreads(self, event):
        for i in range(self.threads_per_click):
            threading.Thread(target=self.producer, args=(i,)).start()


if __name__ == '__main__':
    root = ThreadGui()
    root.mainloop()
