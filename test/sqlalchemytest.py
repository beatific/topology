'''
Created on 2016. 2. 15.

@author: P067880
'''


from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import Sequence
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

Column(Integer, Sequence('user_id_seq'), primary_key=True)

Session = sessionmaker()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
    def __repr__(self):
        return "<User('%s', '%s', '%s')>" % (self.name, self.fullname, self.password)

class LoopbackInfo(Base):
    __tablename__ = 'TB_LOOPBACK'
    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    loopback_yn = Column(Boolean)
    loopback_message = Column(String(4000))
    
    
class Datasource:
    
    def __init__(self):
        self.engine = create_engine('oracle://daram:daram@localhost/orcl', pool_size=20)
        Session.configure(bind=self.engine)
        self.session = Session()

    def create(self):
        Base.metadata.create_all(self.engine)
        
    def add(self, object):
        self.session.add(object)
    
    def query(self, param):
        return self.session.query(param)
        
    def add_all(self, list):
        self.session.add_all(list)
    
    def dirty(self):
        return self.session.dirty
    
    def new(self):
        return self.session.new
    
    def commit(self):
        self.session.commit()
        
    def rollback(self):
        self.session.rollback()
    
if __name__ == '__main__':
    datasource = Datasource()
    datasource.create()
#     ed_user= User('haruair', 'Edward Kim', '1234')
#     datasource.add(ed_user)
    
    query = datasource.query(User)
    for user in query.filter("name='wendy'"):
        print user
        
    print query.first()
    print query.all()
#     
#     datasource.add_all([
#         User('wendy', 'Wendy Williams', 'foobar'),
#         User('mary', 'Mary Contrary', 'xxg527'),
#         User('fred', 'Fred Flinstone', 'blar')])
#     
#     ed_user.password = 'test1234'
#     print datasource.dirty()
#     print datasource.new()
#     
#     datasource.commit()
    
    
    
