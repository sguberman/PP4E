import threading, queue, time


safeprint = threading.Lock()
dataQueue = queue.Queue()
numconsumers = 2
numproducers = 4
nummessages = 4


def producer(idnum, dataqueue):
    for msgnum in range(nummessages):
        time.sleep(idnum)
        dataqueue.put('[producer id={}, count={}]'.format(idnum, msgnum))


def consumer(idnum, dataqueue):
    while True:
        time.sleep(0.1)
        try:
            data = dataqueue.get(block=False)
        except queue.Empty:
            pass
        else:
            with safeprint:
                print('consumer', idnum, 'got =>', data)


if __name__ == '__main__':
    for i in range(numconsumers):
        thread = threading.Thread(target=consumer, args=(i, dataQueue))
        thread.daemon = True
        thread.start()

    waitfor = []
    for i in range(numproducers):
        thread = threading.Thread(target=producer, args=(i, dataQueue))
        waitfor.append(thread)
        thread.start()

    for thread in waitfor:
        thread.join()
    print('Main thread exit.')
