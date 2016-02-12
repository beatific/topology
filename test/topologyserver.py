'''
Created on 2016. 1. 13.

@author: beatific J
'''
import unittest

from topology.topology import Topology
from util.argument import ArgumentParser
from util.config import Config


#from guppy.heapy import RM
class Test(unittest.TestCase):

    def testTopology(self):
        args = ['topology.py', '--config', 'C:/Users/Administrator/git/topology/server.cfg']
        
        parser = ArgumentParser(args)
        parser.mandatory = '--config'
        parser.usage = 'topology.py --config <configfile>'
        map = parser.map
        config = Config(map['config'])

        Topology.start(config)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()