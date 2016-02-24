'''
Created on 2016. 1. 13.

@author: beatific J
'''

from SocketServer import TCPServer
import threading

from sqlalchemy import Column, String, Integer
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from util.queue import QueueManager
from util.tcp import Socket

from base import Devider
from base import Receiver
from base import Sender
from base import ThreadingMixIn
from util.cache import cachable
from util.db import Datasource
from util.speed import SpeedChecker, speed_test

class QueueReceiver(Receiver, SpeedChecker):
    
    daemon_threads = False

    def __init__(self, config, params=None):
        SpeedChecker.__init__(self)
        Receiver.__init__(self, config, params)
        self.request_queue_name = config.config('request_queue')
        self.response_queue_name = config.config('response_queue')
        self.queue_address = config.config('queue_address')
        self.start()
        
    def get_connection(self):
#         data = self.queue().get('message')
#         return self.queue(), data
        return (None, None)
    
#     @speed_test
    def handle(self, queue, data, server):
        
        queue = QueueManager(self.queue_address)
        queue.connect()
        data = queue.get(self.request_queue_name)
        print 'message get{%s}' % data
        self.local.message = data
        
        response = self.process()
        
        queue.put(self.response_queue_name, response)
        
        queue.disconnect()
        
    def receive(self, key):
        return self.local.message
    
class TCPReceiver(TCPServer, Receiver, SpeedChecker):
    
    daemon_threads = False
    
    def __init__(self, config, params=None):
        
        SpeedChecker.__init__(self)
        Receiver.__init__(self, config, params)
        TCPServer.__init__(self, (config.config('ip'), int(config.config('port'))), self.handle, bind_and_activate=False)
        self.request_queue_size =int(config.config('threads'))
        self.server_bind()
        self.server_activate()
        self.start()
        
    @speed_test
    def handle(self, request, client_address, server):
        
        self.local.message = self.receive_data(request)
        
        response = self.process()
        
        request.sendall(response)
        
    def handle_error(self, request, client_address):
        self.exception_handler.handle('Exception happened during processing of request from %s' % client_address)
    
    def start(self):
        t = threading.Thread(target = self.serve_forever, args = ())
        t.daemon = self.daemon_threads
        t.start()
        
    def receive_data(self, request, size=1024):
    
        received = ''
        
        while True: 
            data = request.recv(size)
              
            received += str(data)
            
            if len(data) < size: 
                return received;    
            
    def receive(self, key=None):
        return self.local.message

        
class ThreadingTCPReceiver(ThreadingMixIn, TCPReceiver):
    def __init__(self, config, params=None):
        TCPReceiver.__init__(self, config, params)
        ThreadingMixIn.__init__(self, config)
        
class ThreadingQueueReceiver(ThreadingMixIn, QueueReceiver): 
    def __init__(self, config, params=None):
        ThreadingMixIn.__init__(self, config)
        QueueReceiver.__init__(self, config, params)
        
class QueueSender(Sender):

    def __init__(self, config, params=None):
        Sender.__init__(self, config, params)
        self.request_queue_name = config.config('request_queue')
        self.response_queue_name = config.config('response_queue')
        self.queue_address = config.config('queue_address')
        
    def send(self, message):
        queue = QueueManager(self.queue_address)
        queue.connect()
        queue.put(self.request_queue_name, message)
        data = queue.get(self.response_queue_name)
        queue.disconnect()
        return data
    
        
class TCPSender(Sender):

    def __init__(self, config, params=None):
        Sender.__init__(self, config, params)
        self.ip = config.config('ip')
        self.port = int(config.config('port'))
    
    def send(self, message):
        
        sock = Socket(self.ip, self.port)
        sock.connect()
        sock.send(message)
        data = sock.receive()
        sock.close()
        
        return data

Base = declarative_base()

class TCPConnectionSender(Sender):

    def __init__(self, config, params=None):
        Sender.__init__(self, config, params)
        self.ip = config.config('ip')
        self.port = int(config.config('port'))
        self.sock = Socket(self.ip, self.port)
        self.sock.connect()
    
    def send(self, message):
        
        self.sock.send(message)
        data = self.sock.receive()
        
        return data
    
    def inner_shutdown(self):
        self.sock.close()

Base = declarative_base()


class LoopbackInfo(Base):
    __tablename__ = 'TB_LOOPBACK'
    id = Column(String(50), primary_key=True)
    name = Column(String(100))
    loopback_yn = Column(String(1))
    loopback_message = Column(String(4000))


class LoopbackResult(Base):
    __tablename__ = 'TB_LOOPBACK_RESULT'
    seq = Column(Integer, Sequence('loopback_result_seq'), primary_key=True)
    id = Column(String(50))
    request_message = Column(String(4000))
    loopback_message = Column(String(4000))
    real_message = Column(String(4000))
    process_status = Column(String(1))
    
    def __init__(self, id, request_message, loopback_message):
        self.id = id
        self.request_message = request_message
        self.loopback_message = loopback_message
        self.process_status = 'N'

class Loopback(Devider):
    def __init__(self, config, params=None):
        Devider.__init__(self, config)
        self.id = config.properties('id')
    
    @cachable
    def database(self, id):
        ds = Datasource()
        
        loopback_yn = False
        loopback_message = ''
         
        for  info in ds.query(LoopbackInfo).filter("id='%s'" % id):
            if info.loopback_yn == 'Y':
                loopback_yn = True
            else :
                loopback_yn = False
                
            loopback_message = info.loopback_message
            break
        
        return loopback_yn, loopback_message

    def condition(self, parent, params):
        self.info = self.database(self.id)
        return not self.info[0]
    
    def ifnot(self, parent, params):
        ds = Datasource()
        ds.add(LoopbackResult(self.id, params, self.info[1]))
        return self.info[1]

class LoopbackReceiver(Receiver):
    
    daemon_threads = False

    def __init__(self, config, params=None):
        Receiver.__init__(self, config, params)
        self.data = []
        self.id = config.properties('id')
        
        ds = Datasource()
        for result in  ds.query(LoopbackResult).filter("id='%s'"%self.id).filter("process_status='N'"):
            self.data.append(result)
            
        self.start()
        
    def get_connection(self):
        
        result = self.data.pop()
        
        if not self.data: 
            self._shutdown_request = True
            
        return result.seq, result
    
    def handle(self, seq, result, server):
        
        self.local.message = result.request_message
        response = self.process()
        
        ds = Datasource()
        ds.query(LoopbackResult).\
        filter(LoopbackResult.seq == result.seq).\
        update({"real_message": response, "process_status" : "Y"})
        
    def receive(self, key):
        return self.local.message