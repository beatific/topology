'''
Created on 2016. 2. 16.

@author: P067880
'''
import time
import sys

class Cache:
    
    cache = {}
    

    def __init__(self, interval):
        '''
            @param interval (unit / seconds)
        '''
        self.interval = interval
    
    def hit(self, key):
        
        try:
            if self.cache[key]:
                (valid_time, value) = self.cache[key]
                
                if valid_time  >= time.time():
                    return value
        except KeyError:
            pass
        
        
    
    def register(self, key, value):
        
        self.cache[key] = (time.time() + self.interval, value)
        
    def caching(self, func, *args, **kwargs):
        
        result = self.hit(args)
        
        if result:
            return result
        
        result = func(*args, **kwargs)
        
        self.register(args, result)
        
        return result


cache = Cache(60)

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