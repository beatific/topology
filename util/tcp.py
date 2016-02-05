'''
Created on 2016. 1. 8.

@author: beatific J
'''

import socket
import threading


class Socket(object):
    
    def __init__(self, ip, port, request_size = 10):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.address = (ip, port)
        self.client = None
        self.caddress = None
        self.request_size = request_size
        self.local = threading.local()
        
    def connect(self):
        try:
            if not self.local.conn:
                self.sock.connect(self.address)
        except AttributeError:
            self.sock.connect(self.address)
        
        self.local.conn = self.sock
    
    def listen(self):
        self.sock.bind(self.address)
        self.sock.listen(self.request_size)
    
    def send(self, message):
        self.local.conn.sendall(message)

    
    def accept(self):
        self.client, self.caddress = self.sock.accept()
        self.local.conn = self.client
    
    def receive(self, size=1024):
        
        received = ''
        
        while True: 
            data = self.local.conn.recv(size)
              
            received += str(data)
            
            if len(data) < size: 
                return received;
    
    def close(self):
        self.local.conn.close()
        