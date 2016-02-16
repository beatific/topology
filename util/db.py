'''
Created on 2016. 2. 15.

@author: P067880
'''

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
Session = sessionmaker()

class Datasource:
    
    def __init__(self, address, pool_size=10):
        self.engine = create_engine(address, pool_size=pool_size)
        Session.configure(bind=self.engine)
        self.session = Session()

    def add(self, obj):
        self.session.add(obj)
        
    def add_all(self, objs):
        self.session.add_all(objs)
        
    def query(self, param):
        return self.session.query(param)
    
    def dirty(self):
        return self.session.dirty
    
    def new(self):
        return self.session.new
    
    def commit(self):
        self.session.commit()
        
    def rollback(self):
        self.session.rollback()
        