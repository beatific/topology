'''
Created on 2016. 1. 13.

@author: beatific J
'''

from Queue import Queue
from SocketServer import TCPServer
import sys
import threading
import time

from base import Receiver
from base import Sender
from base import ThreadingMixIn
from util.tcp import Socket
from util.queue import QueueManager


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


    
class QueueReceiver(Receiver):
    
    daemon_threads = False
    size = 10

    def __init__(self, params=None):
        Receiver.__init__(self, params)
        self.request_queue_name = 'message'
        self.response_queue_name = 'response'
        self.start()
        
    def queue(self):
        try :
            if self.local.queue :
                pass
            
        except AttributeError:
            self.local.queue = QueueManager('localhost')
            self.local.queue.connect()
            
        return self.local.queue
    
    def get_connection(self):
        data = self.queue().get('message')
        return self.queue(), data
    
    @speed_test
    def handle(self, queue, data, server):
        print >>sys.stderr, 'get message'
        self.local.message = data
        print >>sys.stderr, 'server : received "%s"' % self.local.message
        
        response = self.process()
        
        self.queue().put(self.response_queue_name, response)
        
    def receive(self, key):
        return self.local.message
        
class TCPReceiver(TCPServer, Receiver):
    
    HOST, PORT, size= "localhost", 1000, 10
    daemon_threads = False
    
    def __init__(self, params=None):
        Receiver.__init__(self, params)
        TCPServer.__init__(self, (self.HOST, self.PORT), self.handle, bind_and_activate=False)
        self.request_queue_size = self.size
        self.server_bind()
        self.server_activate()
        self.q = Queue() #using speed_test
        self.q.put({'count':0, 't1':None, 't2':None}) #using speed_test
        self.start()
        
    @speed_test
    def handle(self, request, client_address, server):
        
        print >>sys.stderr, 'receive message'
        self.local.message = self.receive_data(request)
        print >>sys.stderr, 'server : received "%s"' % self.local.message
        
        response = self.process()
        
        request.sendall(response)
        print >>sys.stderr, 'server : sent "%s"' % response
    
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
                print received
                return received;    
            
    def receive(self, key=None):
        return self.local.message

        
class ThreadingTCPReceiver(ThreadingMixIn, TCPReceiver):
    def __init__(self, params=None):
        TCPReceiver.__init__(self, params)
        ThreadingMixIn.__init__(self)
        
class ThreadingQueueReceiver(ThreadingMixIn, QueueReceiver): 
    def __init__(self, params=None):
        QueueReceiver.__init__(self, params)
        ThreadingMixIn.__init__(self)
        
class QueueSender(Sender):

    def __init__(self, params):
        Sender.__init__(self, params)
    
    def queue(self):
        try :
            if self.local.queue :
                pass
            
        except AttributeError:
            self.local.queue = QueueManager('localhost')
            self.local.queue.connect()
            
        return self.local.queue
        
    def send(self, message):
        
        self.queue().put('message', message)
        return self.queue().get('response')
        
    def shutdwon(self):
        self.queue().disconnect()
        
class TCPSender(Sender):

    HOST, PORT, REQUEST_SIZE= "localhost", 1000, 10
    
    def __init__(self, params):
        Sender.__init__(self, params)
    
    def send(self, message):
        
        sock = Socket(self.HOST, self.PORT)
        sock.connect()
        print 'message %s' % message
        sock.send(message)
        data = sock.receive()
        print 'data %s' % data
        sock.close()
        
        return data