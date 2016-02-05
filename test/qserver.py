'''
Created on 2016. 1. 8.

@author: beatific J
'''
from Queue import Queue
import threading
import time
import unittest

from util.pool import ThreadPool
from util.queue import QueueManager

#from guppy.heapy import RM


lock = threading.Lock()

def speed_test(func):
    def wrapper(*args, **kwargs):
        
        self = args[0]
        
        with lock:       
            arg = self.q.get()
            print 'count %s' % arg['count']
            if arg['count'] == 0: 
                arg['t1'] = time.time()
            arg['count'] = arg['count'] + 1 
            self.q.put(arg)

        results = func(*args, **kwargs)
        
        with lock:
            arg = self.q.get()
            if arg['count'] == 1000: 
                arg['count'] = 0
                arg['t2'] = time.time()
                print '======================================%s took %0.3f ms======================================' % (func.func_name, (arg['t2']-arg['t1'])*1000.0)
                print '====================================== %0.3f tps======================================' % (1000 / (arg['t2']-arg['t1']))
            self.q.put(arg)
            
        return results
    return wrapper

class Test(unittest.TestCase):

    def setUp(self):
        self.p = ThreadPool(10)
        self.q = Queue() #using speed_test
        self.q.put({'count':0, 't1':None, 't2':None}) #using speed_test
            
    def tearDown(self):
        pass

    def test(self):
        while True:
            self.p.apply(self.get_and_put, args=())
    
    @speed_test
    def get_and_put(self):
        queue = QueueManager('localhost')
        queue.connect()
        data = queue.get('message')
#         time.sleep(0.02)
        print data
        queue.put('response', 'queue[%s]' % data)
        queue.disconnect()

if __name__ == "__main__":
    unittest.main()