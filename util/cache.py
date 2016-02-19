'''
Created on 2016. 2. 16.

@author: P067880
'''
import threading
import time
import sys

class Cache:
    
    cache = {}
    cache_list = []

    def __init__(self, interval=60):
        '''
            @param interval (unit / seconds)
        '''
        self.interval = interval
        self.working = False
        self.lock = threading.Lock()
        
    def start(self):
        with self.lock:
            if not self.working:
                t = threading.Thread(target=self.cache_loop, args=())
                t.start()
        
    def stop(self):
        with self.lock:
            self.working = False
    
    def hit(self, key):
        
        try:
            if self.cache[key]:
                return self.cache[key]
            
        except KeyError:
            pass
        
        
    
    def register(self, key, value):
        
        self.cache[key] = value
        
    def cache_loop(self):
        
        with self.lock:
            self.working = True
        
        while self.working:
            
            for (func, args, kwargs) in self.cache_list:
                try:
                    result = func(*args, **kwargs)
                    
                    self.register(args, result)
                except Exception as e:
                    print >>sys.stderr,  e
            
            time.sleep(self.interval)
        
    def caching(self, func, *args, **kwargs):
        
        result = self.hit(args)
        
        if result:
            return result
        
        result = func(*args, **kwargs)
        self.cache_list.append((func, args, kwargs))
        self.register(args, result)
        self.start()
        
        return result


cache = Cache()

def cachable(func):
    
    def wrapper(*args, **kwargs):
        
        result = cache.caching(func, *args, **kwargs)
        return result
    
    return wrapper


def main():
    for i in range(10) :
        print time.time(), time.time() + 0.01
        time.sleep(1)

if __name__ == '__main__' :
    main()