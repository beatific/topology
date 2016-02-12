'''
Created on 2016. 2. 5.

@author: P067880
'''

import sys

class ArgumentParser(object):
    
    def __init__(self, args, validation=False):
        self._mandatories = []
        self._options =[]
        self._usage = ""
        self._args = args
        self._validation = validation

    @property
    def option(self):
        return self._options
    
    @property
    def mandatory(self):
        return self._mandatories
    
    @property
    def usage(self):
        return self._usage
        
    @option.setter    
    def option(self, option):
        self._set_option(option, self._options)
    
    @mandatory.setter
    def mandatory(self, option):
        self._set_option(option, self._mandatories)
        
    def _set_option(self, option, options):
        if not isinstance(option, list):
            option = [option]
        
        option =  map(lambda x: x.replace('--', ''), option)
        options.extend(option)
        self._validation = True
    
    @usage.setter
    def usage(self, usage):
        self._usage = usage
        
    def _arguemnt_dict(self, args):
    
        if len(args) < 2:
            self._exception()
        
        dict = {}  # @ReservedAssignment
        dict[args[0].replace('--', '')] = args[1]
        
        if len(args) > 2:
            dict.update(self._arguemnt_dict(args[2:]))
            
        return dict
    
    def _exception(self):
        if self._usage:
            print >>sys.stderr, '[Usage]', self._usage
        else:
            print >>sys.stderr, 'not exists designated usage!'
        sys.exit(1)
    
    def _validate(self, dict):
        
        # mandatory value
        if set(self._mandatories) - set(dict.keys()):
            self._exception()
        
        # the list of all options
        if set(dict.keys()) - (set(self._mandatories) | set(self._options)) :
            self._exception()
        
    @property
    def map(self):
    
        if len(self._args) < 3:
            self._exception()
        
        dict = self._arguemnt_dict(self._args[1:])  
        if self._validation:
            self._validate(dict)
            
        return dict

def test():
    try:
        args = ['test', '--config', 'C:/data/projects/daram/workspaces/topology/server.cfg']
        parser = ArgumentParser(args)
        parser.mandatory = '--config'
        print parser.map
    except Exception as e:
        print e
    
if __name__ == "__main__":
    test()
    