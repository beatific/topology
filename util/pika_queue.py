'''
Created on 2016. 1. 29.

@author: P067880
'''

import pika

from util.pool import ThreadPool
import threading, time

class QueueManager(object):
    
    def __init__(self, host):
        self._connection = None
        self._channel = None
        self._url = host
        
    def connect(self):
            parameters = pika.URLParameters('amqp://' + self._url + '/%2F')
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
        
    def get(self, qname):
        
        method_frame, header_frame, body = self._channel.basic_get(qname)
        if method_frame:
            self._channel.basic_ack(method_frame.delivery_tag)
        else:
            print('No message returned')
        return body

    
    def put(self, qname, message):
        
        success = self._channel.basic_publish(exchange='', routing_key=qname, body=message)
        return success
        
    def disconnect(self):
        if self._channel:
            self._channel.close()
            
        if self._connection:
            self._connection.close()

def test():
    q= QueueManager('localhost')
    q.connect()
    q.put('message', 'hello')
    q.disconnect()
    
    q= QueueManager('localhost')
    q.connect()
    print q.get('message')
    q.disconnect()
        
def main():
    test()
#     print 'main'
#     p = ThreadPool(10)
#     while True :
#         p.apply_async(func=test, args=())
    
if __name__ == "__main__":
    main()