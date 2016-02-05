'''
Created on 2016. 2. 4.

@author: P067880
'''
from ConfigParser import ConfigParser
import json
from collections import namedtuple


class Config(object):

    def __init__(self, filename):
        self.cfg = ConfigParser()
        self.cfg.read(filename)
    
    def topology(self):
        
        path = self.cfg.get('topology', 'path')
        topology = json.loads(open(path, 'r').read())
        
        return topology
    
    def config(self, key):
        return self.cfg.get('config', key)
    
    def properties(self, key):
        return self.cfg.get('properties', key)
    
def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def main():
    try:
        config = Config('C:/data/projects/daram/workspaces/topology/server.cfg')
        print 'topology[%s]' % config.topology()
        print config.config('ip')
        print config.config('port')
        print config.properties('loopback')

    except  Exception as e:
        print e
    
if __name__ == "__main__":
    main()