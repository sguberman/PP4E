"""
##############################################################################
System-wide thread interface utilities for GUIs.

Implements a single thread callback queue and checker timer loop shared by
all the windows in a program; worker threads queue their exit and progress
actions to be run in the main thread; this doesn't block the GUI - it just
spawns operations and manages and dispatches exits and progress; worker
threads can overlap freely with the main thread, and with other workers.

Using a queue of callback functions and arguments is more useful than a
simple data queue if there can be many kinds of threads running at the
same time - each kind may have different implied exit actions.

Because GUI API is not completely thread-safe, instead of calling GUI
update callbacks directly after thread main action, place them on a shared
queue, to be run from a timer loop in the main thread, not a child thread;
this also makes GUI update points less random and unpredictable; requires
threads to be split into main action, exit actions, and progress action.

Assumes threaded action raises an exception on failure, and has a 'progress'
callback argument if it supports progress updates; also assumes callbacks
are either short-lived or update as they run, and that queue will contain
callback functions (or other callables) for use in a GUI app - requires a
widget in order to schedule and catch 'after' event loop callbacks; to use
this model in non-GUI contexts, could use simple thread timer instead.
##############################################################################
"""

# run even if no threads
try:
    import _thread as thread
except ImportError:
    import _dummy_thread as thread

# shared cross-process queue
# named in shared global scope, lives in shared object memory
import queue
import sys
threadqueue = queue.Queue(maxsize=0)  # infinite size


"""
##############################################################################
IN MAIN THREAD - periodically check thread completions queue; run implied GUI
actions on queue in this main GUI thread; one consumer (GUI), and multiple
producers (load, del, send); a simple list may suffice too: list.append and
pop atomic? 4E: runs at most N actions per timer event: looping through all
queued callbacks on each timer event may block GUI indefinitely, but running
only one can take a long time or consume CPU for timer events (eg, progress);
assumes callback is either short-lived or updates display as it runs: after a
callback run, the code here reschedules and returns to event loop and updates;
because this perpetual loop runs in main thread, does not stop program exit;
##############################################################################
"""


def threadChecker(widget, delayMsecs=100, perEvent=1):
    for i in range(perEvent):
        try:
            (callback, args) = threadqueue.get(block=False)
        except queue.Empty:
            break
        else:
            callback(*args)

    widget.after(delayMsecs, lambda: threadChecker(widget, delayMsecs, perEvent))


"""
##############################################################################
IN A NEW THREAD - run action, manage thread queue puts for exits and progress;
run action with args now, later run on* calls with context; calls added to
queue here are dispatched in main thread only, to avoid parallel GUI updates;
allows action to be fully ignorant of use in a thread here; avoids running
callbacks in thread directly: may update GUI in thread, since passed func in
shared memory called in thread; progress callback just adds callback to queue
with passed args; don't update in-progress counters here: not finished until
exit actions taken off queue and dispatched in main thread by threadChecker;
##############################################################################
"""


def threaded(action, args, context, onExit, onFail, onProgress):
    try:
        if not onProgress:
            action(*args)
        else:
            def progress(*any):
                threadqueue.put((onProgress, any + context))
            action(progress=progress, *args)
    except:
        threadqueue.put((onFail, (sys.exc_info(),) + context))
    else:
        threadqueue.put((onExit, context))


def startThread(action, args, context, onExit, onFail, onProgress=None):
    thread.start_new_thread(threaded, (action, args, context, onExit, onFail, onProgress))


"""
##############################################################################
a thread-safe counter or flag: useful to avoid operation overlap if threads
update other shared state beyond that managed by the thread callback queue
##############################################################################
"""


class ThreadCounter:
    def __init__(self):
        self.count = 0
        self.mutex = thread.allocate_lock()

    def incr(self):
        self.mutex.acquire()
        self.count += 1
        self.mutex.release()

    def decr(self):
        self.mutex.acquire()
        self.count -= 1
        self.mutex.release()

    def __len__(self):
        return self.count


# self-test code: split thread action into main, exits, progress
if __name__ == '__main__':
    import time
    from tkinter.scrolledtext import ScrolledText


    def onEvent(i):
        myname = 'thread-%s' % i
        startThread(
            action=threadaction,
            args=(i, 3),
            context=(myname,),
            onExit=threadexit,
            onFail=threadfail,
            onProgress=threadprogress
        )


    # thread's main action
    def threadaction(id, reps, progress):
        for i in range(reps):
            time.sleep(1)
            if progress:
                progress(i)
        if id % 2 == 1:
            raise Exception  # fail on odd-numbered ids


    # thread exit/progress callbacks: dispatched off queue in main thread
    def threadexit(myname):
        text.insert('end', '%s\texit\n' % myname)
        text.see('end')


    def threadfail(exc_info, myname):
        text.insert('end', '%s\tfail\t%s\n' % (myname, exc_info[0]))
        text.see('end')


    def threadprogress(count, myname):
        text.insert('end', '%s\tprog\t%s\n' % (myname, count))
        text.see('end')
        text.update()


    # make enclosing GUI and start timer loop in main thread
    # spawn batch of worker threads on each mouse click: may overlap
    text = ScrolledText()
    text.pack()
    threadChecker(text)
    text.bind('<Button-1>', lambda event: list(map(onEvent, range(6))))
    text.mainloop()  # popup window, enter tk event loop
