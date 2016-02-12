'''
Created on 2016. 1. 22.

@author: beatific J
'''
import Queue
from multiprocessing.pool import Pool
from threading import Thread
import threading
import time


class ThreadPool(Pool):
    
    from multiprocessing.dummy import Process
    
    def __init__(self, processes=None, initializer=None, initargs=()):
        Pool.__init__(self, processes, initializer, initargs)
        self._taskqueue.maxsize = self._processes
        self._inqueue.maxsize = self._processes
        self._outqueue.maxsize = self._processes
        
    def _setup_queues(self):
        self._inqueue = Queue.Queue()
        self._outqueue = Queue.Queue()
        self._quick_put = self._inqueue.put
        self._quick_get = self._outqueue.get

    @staticmethod
    def _help_stuff_finish(inqueue, task_handler, size):
        inqueue.not_empty.acquire()
        try:
            inqueue.queue.clear()
            inqueue.queue.extend([None] * size)
            inqueue.not_empty.notify_all()
        finally:
            inqueue.not_empty.release()
        
    
def test():
    t = threading.currentThread()
    print t
    time.sleep(0.2)
    
def main():
    p = ThreadPool(10)
    
    while True :
#         t = Thread(target=test)
#         t.start()
        p.apply_async(func=test, args=())
    
if __name__ == "__main__":
    main()
            