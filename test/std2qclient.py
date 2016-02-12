'''
Created on 2016. 1. 8.

@author: beatific J
'''
from util.queue import QueueManager

def test():
    while True:
        message = raw_input("Enter your message: ")
        put_and_get(message)
    

def put_and_get(message):
    queue = QueueManager('localhost')
    queue.connect()
    queue.put('message', message)
    response = queue.get('response')
    print 'response message:', response
    queue.disconnect()

if __name__ == "__main__":
    test()