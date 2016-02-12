'''
Created on 2016. 1. 13.

@author: beatific J
'''

from Queue import Queue
from SocketServer import TCPServer
import sys
import threading
import time

from util.queue import QueueManager
from util.tcp import Socket

from base import Devider
from base import Receiver
from base import Sender
from base import ThreadingMixIn


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
    
class QueueReceiver(Receiver):
    
    daemon_threads = False

    def __init__(self, config, params=None):
        Receiver.__init__(self, config, params)
        self.request_queue_name = config.config('request_queue')
        self.response_queue_name = config.config('response_queue')
        self.q = Queue() #using speed_test
        self.q.put({'count':0, 't1':None, 't2':None}) #using speed_test
        self.start()
        
    def get_connection(self):
#         data = self.queue().get('message')
#         return self.queue(), data
        return (None, None)
    
    @speed_test
    def handle(self, queue, data, server):
        
        queue = QueueManager('localhost')
        queue.connect()
        data = queue.get(self.request_queue_name)
        self.local.message = data
        
        response = self.process()
        queue.put(self.response_queue_name, response)
        
        queue.disconnect()
        
    def receive(self, key):
        return self.local.message
        
class TCPReceiver(TCPServer, Receiver):
    
    daemon_threads = False
    
    def __init__(self, config, params=None):
        
        Receiver.__init__(self, config, params)
        TCPServer.__init__(self, (config.config('ip'), int(config.config('port'))), self.handle, bind_and_activate=False)
        self.request_queue_size =int(config.config('threads'))
        self.server_bind()
        self.server_activate()
        self.q = Queue() #using speed_test
        self.q.put({'count':0, 't1':None, 't2':None}) #using speed_test
        self.start()
        
    @speed_test
    def handle(self, request, client_address, server):
        
#         print >>sys.stderr, 'receive message'
        self.local.message = self.receive_data(request)
#         print >>sys.stderr, 'server : received "%s"' % self.local.message
        
        response = self.process()
        
        request.sendall(response)
#         print >>sys.stderr, 'server : sent "%s"' % response
    
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
        
        
    def send(self, message):
        queue = QueueManager('localhost')
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

class Loopback(Devider):
    def __init__(self, config, params=None):
        Devider.__init__(self, config)
        self.loopback_yn = bool(config.properties('loopback'))
        self.loopback_message = config.properties('loopback_message')

    def condition(self, parent, params):
        return not self.loopback_yn
    
    def ifnot(self, parent, params):
        return self.loopback_message
        