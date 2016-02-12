'''
Created on 2016. 1. 11.

@author: beatific J
'''

import sys

from base import Leaf
from base import Root
from exception import ExceptionHandler
import node
from util.config import Config
from util.argument import ArgumentParser


class Topology(object):

    def __init__(self):
        self.handler = ExceptionHandler()
    
    @staticmethod
    def start(config):
        
        TopologyBuilder.build(config)
        
    def progress(self):
        
        data = None
        try :
            self.inner_progress(self.root, data)
        except Exception as e:
            self.handler.handle(e)

    def inner_progress(self, node, data):
        
        for child in node.children :
            data = child.process(node, data)
            self.inner_progress(child, data)
            node.response(child.result)
            
class TopologyBuilder(object):

    numberingObjects = {}
    
    @staticmethod    
    def prebuild(config):
        
        if not type(config) is Config :
            raise Exception('TpologyBuilder.prebuild: config must be Config type. real [%s]' % type(config))
        
        root = Root()
        TopologyBuilder.numberingObjects[0] = root
        
        topology = config.topology()
        if not type(topology) is list :
            raise Exception('TpologyBuilder.prebuild: topology must be list type. real [%s]' % type(topology))
        
        for definition in topology:
            TopologyBuilder.prebuilds(definition, config)
    
    @staticmethod
    def prebuilds(definition, config):
        
        if not type(definition) is dict :
            raise Exception('TpologyBuilder.prebuilds: node definition must be dictionary. real [%s]' % type(definition))
        
        num = definition['num']
        children = definition['children']
        name = definition['class']
        root_yn = definition['root']
            
        node = TopologyBuilder.newinstance(name, config)
        node.add_children(children)
        
        TopologyBuilder.numberingObjects[num] = node
        
        if root_yn :
            TopologyBuilder.numberingObjects[0].add_child(num)
    
    @staticmethod
    def build(config):
       
        leaf = Leaf() 
        t = Topology()
        
        TopologyBuilder.prebuild(config)
        
        for num, node in TopologyBuilder.numberingObjects.items() :

            if num == 0 :
                root = node
                            
            children = []

            for child in node.children :
                children.append(TopologyBuilder.numberingObjects[child])
                TopologyBuilder.numberingObjects[child].add_parent(node)
                
            node.clear_children()
            node.add_children(children)
            
            if not node.children :
                node.add_child(leaf)
                leaf.add_parent(node)
            
        TopologyBuilder.numberingObjects = None
        t.root = root
        return t
    
    @staticmethod
    def newinstance(classname, config):
        names = classname.split('.')
        module = globals()[names[0]]
        
        module_names = names[1:]
        for name in module_names :
            module = getattr(module, name)
            
        return module(config) 


def main():
    parser = ArgumentParser(sys.argv)
    parser.mandatory = '--config'
    parser.usage = 'topology.py --config <configfile>'
    map = parser.map
    config = Config(map['config'])
    
    Topology.start(config)
    
if __name__ == "__main__":
    main()
    