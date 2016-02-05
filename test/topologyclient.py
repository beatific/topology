'''
Created on 2016. 1. 13.

@author: beatific J
'''
import unittest
from topology.topology import Topology
#from guppy.heapy import RM

class Test(unittest.TestCase):

    def testTopology(self):
        
        docs = [{'num': 1, 'root' : True, 'children':[2], 'class' : 'node.ThreadingQueueReceiver'}, 
                {'num': 2, 'root' : False, 'children':[], 'class' : 'node.TCPSender'}]
        
#         docs = [{'num': 1, 'root' : True, 'children':[2], 'class' : 'receiver.QueueReceiver'}, 
#                 {'num': 2, 'root' : False, 'children':[], 'class' : 'sender.TCPSender'}]

        Topology.start(docs)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()