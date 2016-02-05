'''
Created on 2016. 1. 8.

@author: beatific J
'''

import threading

import pika.spec as spec
import puka 

from util.pool import ThreadPool


class QueueManager(object):
    
    local = threading.local()

    def __init__(self, host):
        
        try:
            if not self.local.queue :
                self.local.queue = puka.Client("amqp://"+ host + "/")
                self.connect()
                self.local.properties = spec.BasicProperties()
        except AttributeError:
            print 'init'
            self.local.queue = puka.Client("amqp://"+ host + "/")
            self.connect()
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
        
def test():
    q = QueueManager('localhost')
#     q.connect()
    q.put('message', 'hello')
    q.get('message')
#     q.disconnect()

def main():
    print 'main'
    p = ThreadPool(10)
    while True :
        p.apply_async(func=test, args=())
    
if __name__ == "__main__":
    main()
       
        