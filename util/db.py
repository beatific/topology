'''
Created on 2016. 2. 15.

@author: P067880
'''

from Queue import Queue

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


Session = scoped_session(sessionmaker())

class Datasource:
    
    @staticmethod
    def config(address, pool_size=10):
        engine = create_engine(address, pool_size=pool_size)
        Session.configure(bind=engine)
        
    def __init__(self):
        self.session = Session()

    def add(self, obj):
        self.session.add(obj)
        
    def add_all(self, objs):
        self.session.add_all(objs)
        
    def query(self, param=None):
        if param == None:
            return self.session.query()
        
        return self.session.query(param)
    
    def dirty(self):
        return self.session.dirty
    
    def new(self):
        return self.session.new
    
    def commit(self):
        self.session.commit()
        
    def rollback(self):
        self.session.rollback()


def test(q):
    
    ds1 = Datasource()
    q.put(ds1)
    ds2 = Datasource()
    q.put(ds2)

def main():
    Datasource.config('oracle://daram:daram@localhost/orcl', 10)
    
    q = Queue()
    
    ds1 = Datasource()
    ds2 = Datasource()
    
    print ds1.session == ds2.session
    
    import threading
    
    l = []
    
    for i in range(10):
        
        t = threading.Thread(target = test, args = ([q]))
        l.append(t)
        t.start()
        
    for t in l:
        t.join()
    
    ds_list = []
    for i in range(q.qsize()):
        ds = q.get()
        ds_list.append(ds)
        
    for i in range(len(ds_list)-1):
        print ds_list[i].session == ds_list[i+1].session
    
if __name__ == '__main__':
    main()
