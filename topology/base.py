'''
Created on 2016. 1. 22.

@author: beatific J
'''
from abc import abstractmethod
import threading

from exception import DefaultExceptionHandler
from util.pool import ThreadPool

from util.db import Datasource


class Node(object):
    
    def __init__(self, type, config=None, handler=DefaultExceptionHandler()):
        
        self.root = False
        self.parents = []
        self.children = []
        self.type = type
        self.local = threading.local()
        self.config = config
        self.exception_handler = handler
        
    def add_child(self, child):
        if child is None : 
            return
        
        self.children.append(child)
        
    def add_children(self, children):
        
        if children is None : 
            return
        
        if not type(children) is list :
            raise Exception('Node.add_children : Child of Node must be List. real [%s]' % type(children))
        
        self.children[len(self.children):] = children
        
    def clear_children(self):
        self.children = []

    def add_parent(self, parent):
        
        if parent is None : 
            return
        
        self.parents.append(parent)
        
    def add_parents(self, parents):
        if parents is None : 
            return
        
        if type(parents) is not list :
            raise Exception('Node.add_parents : parent of Node must be List. real [%s]' % type(parents))
        
        self.parents[len(self.parents):] = parents
    
    @abstractmethod
    def inner_process(self, parent, params):
        pass
    
    def process(self, parent=None, params=None):
        
        results = []
        try:
            data = self.inner_process(parent, params)
            for child in self.children:
                results.append(child.process(self, data))
            return self.convert(results)
        except Exception as ex:
            self.exception_handler.handle(ex)
    
    def convert(self, results):
        
        return results[0]
    

    @abstractmethod    
    def inner_shutdown(self):
        pass
        
    def stop(self):
        self.inner_shutdown()
        for child in self.children:
            child.stop()

class Root(Node):

    def __init__(self, params=None):
        Node.__init__(self, 'root')
        self.root = True
        self.leaf = False
        
    def inner_process(self, parent, params):
        pass

class Leaf(Node):
    
    def __init__(self, params=None):
        Node.__init__(self, 'leaf')
        self.root = False
        self.leaf = True
        
    def process(self, parent, params):
        return params

class Receiver(Node):

    def __init__(self, config, params=None):
        Node.__init__(self, 'receiver', config)
        
        self._is_shut_down = threading.Event()
        self._shutdown_request = False
        
    def inner_process(self, parent, params):
        return self.receive(params)
    
    def start(self):
        try :
            t = threading.Thread(target = self.serve_forever, args = ())
            t.daemon = self.daemon_threads
            t.start()
        except Exception as ex:
            self.exception_handler.handle(ex)
        
    def serve_forever(self):
        self._is_shut_down.clear()
        try:
            while not self._shutdown_request:
                self._handle_request_noblock()
        except Exception as ex:
            self.exception_handler.handle(ex)
        finally:
            self._shutdown_request = False
            self._is_shut_down.set()
            
    def _handle_request_noblock(self):
        
        connection, data = self.get_connection()
        if self.verify_request(connection, data):
            try:
                self.process_request(connection, data)
            except Exception as ex:
                self.exception_handler.handle(ex)
                self.shutdown_request(connection)

    def shutdown(self):
        self._shutdown_request = True
        self._is_shut_down.wait()
        
    def verify_request(self, connection, data):
        return True
    
    def process_request(self, connection, data):
        try:
            ds = Datasource()
            self.finish_request(connection, data)
            self.shutdown_request(connection)
            ds.commit()
        except Exception as ex:
            ds.rollback()
            self.exception_handler.handle(ex)
            self.shutdown_request(connection)
    
    def finish_request(self, connection, data):
        self.handle(connection, data, self)
        
    def shutdown_request(self, connection):
        self.close_request(connection)
        
    def close_request(self, connection):
        pass
    
    def server_activate(self):
        pass
    
    @abstractmethod
    def get_connection(self):
        pass
    
    @abstractmethod
    def handle(self, connection, data, server):
        pass
        
    @abstractmethod
    def receive(self, params):
        pass

class ThreadingMixIn:
    
    def __init__(self, config):
        self.pool = ThreadPool(processes=int(config.config('threads')))
    
    def process_request_thread(self, request, client_address):
        try:
            ds = Datasource()
            self.finish_request(request, client_address)
            self.shutdown_request(request)
            ds.commit()
        except Exception as ex:
            ds.rollback()
            self.exception_handler.handle(ex)
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        self.pool.apply_async(func=self.process_request_thread, args=(request, client_address))

class Sender(Node):

    def __init__(self, config, params=None):
        Node.__init__(self, 'sender', config)
        
    def inner_process(self, parent, params):
        return self.send(params)
        
    @abstractmethod
    def send(self, params):
        pass
    
class Devider(Node):
    def __init__(self, config, params=None):
        Node.__init__(self, 'devider', config)

    def inner_process(self, parent, params):
        return params
    
    def process(self, parent=None, params=None):
        condition = self.condition(parent, params)
        if condition:
            return self.ifthen(condition, parent, params)
        else :
            return self.ifnot(parent, params)
    
    def ifthen(self, condition, parent, params):
        return Node.process(self, parent, params)
    
    @abstractmethod 
    def condition(self, parent, params):
        pass
    
    @abstractmethod
    def ifnot(self, parent, params):
        pass
