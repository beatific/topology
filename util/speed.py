'''
Created on 2016. 2. 18.

@author: P067880
'''
from Queue import Queue
import threading
import time


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
            if arg['count'] % 1000 == 0: 
                arg['t2'] = time.time()
                print '====================================== %0.3f tps======================================' % (arg['count'] / (arg['t2']-arg['t1']))
            self.q.put(arg)
            
        return results
    return wrapper

class SpeedChecker:
    def __init__(self):
        self.q = Queue() #using speed_test
        self.q.put({'count':0, 't1':None, 't2':None}) #using speed_test