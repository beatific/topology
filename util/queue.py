'''
Created on 2016. 1. 8.

@author: beatific J
'''

from Queue import Queue
from socket import errno
import socket
import threading
import time

from puka import machine
import puka 
from puka.connection import set_ridiculously_high_buffers, set_close_exec
from util.pool import ThreadPool

import pika.spec as spec


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

class QueueManager(object):
    
    local = threading.local()

    def __init__(self, host):
        
#         try:
#             if not self.local.queue :
#                 self.local.queue = puka.Client("amqp://"+ host + "/")
#                 self.connect()
#                 self.local.properties = spec.BasicProperties()
#         except AttributeError:
#             print 'init'
        self.local.queue = PukaQueue("amqp://"+ host + "/")
#             self.connect()
        self.local.properties = spec.BasicProperties()
        
    def connect(self):
        
        promise = self.local.queue.connect()
        self.local.queue.wait(promise)
        
    def get(self, qname):
        
        promise = self.local.queue.basic_consume(queue=qname, prefetch_count=1)
        
#         while True:
        received_message = self.local.queue.wait(promise)
        self.local.queue.basic_ack(received_message)
        
        promise = self.local.queue.basic_cancel(promise)
        self.local.queue.wait(promise)
          
        return received_message['body']

    
    def put(self, qname, message):
        
#         promise = self.local.queue.queue_declare(queue=qname)
#         self.local.queue.wait(promise)
        
        promise = self.local.queue.basic_publish(exchange='', routing_key=qname, body=message)
        self.local.queue.wait(promise)
        
    def disconnect(self):
        promise = self.local.queue.close()
        self.local.queue.wait(promise)
        
        print 'disconnect'

class PukaQueue(puka.Client):
    def _connect(self):
        self._handle_read = self._handle_conn_read
        self._init_buffers()

#         addrinfo = None
#         if socket.has_ipv6:
#             try:
#                 addrinfo = socket.getaddrinfo(
#                     self.host, self.port, socket.AF_INET6, socket.SOCK_STREAM)
#             except socket.gaierror:
#                 pass
#         if not addrinfo:
#             addrinfo = socket.getaddrinfo(
#                 self.host, self.port, socket.AF_INET, socket.SOCK_STREAM)
# 
#         print addrinfo[0]
#         print socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP
#         (family, socktype, proto, canonname, sockaddr) = addrinfo[0]
        self.sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        set_ridiculously_high_buffers(self.sd)
        set_close_exec(self.sd)
        try:
            self.sd.connect(('localhost', 5672))
        except socket.error, e:
            if e.errno not in (errno.EINPROGRESS, errno.EWOULDBLOCK):
                raise

        self.sd.setblocking(False)
        if self.ssl:
            self.sd = self._wrap_socket(self.sd)
            self._needs_ssl_handshake = True

        return machine.connection_handshake(self)

class Test(object):
    
    def __init__(self):
        self.q = Queue() #using speed_test
        self.q.put({'count':0, 't1':None, 't2':None}) #using speed_test
        
    @speed_test        
    def test(self):
        try:    
            q = QueueManager('localhost')
            q.connect()
            q.put('message', 'hello')
            print q.get('message')
            q.disconnect()
            
            q = QueueManager('localhost')
            q.connect()
            q.put('message', 'hello')
            print q.get('message')
            q.disconnect()
        except Exception as ex:
            print ex

def main():
    print 'main'
    p = ThreadPool(10)
    test = Test()
    while True :
        p.apply_async(func=test.test, args=())
    
if __name__ == "__main__":
    main()
       
        