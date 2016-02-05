'''
Created on 2016. 2. 3.

@author: P067880
'''
from distutils.core import setup

py_modules = [
 'topology.topology',
 'topology.node',
 'topology.base',
 'topology.exception',
 'util.pool',
 'util.queue',
 'util.tcp',
 'util.config',
 'util.argument',
]
print 'Topology-Agent modules\n%s' % py_modules
setup (name = 'Topology',
       version = '1.0',
       description = 'Integration Framework',
       py_modules = py_modules)