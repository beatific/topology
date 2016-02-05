from Queue import Queue
import SocketServer
import threading
import time
#from guppy.heapy import RM


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

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    i = 0
    q = Queue() #using speed_test
    q.put({'count':0, 't1':None, 't2':None}) #using speed_test
    
    @speed_test
    def handle(self):
        
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        # just send back the same data, but upper-cased
        
        print 'sleep %d' % ++self.i
        time.sleep(0.02)
        self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "localhost", 2000

    # Create the server, binding to localhost on port 9999
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()