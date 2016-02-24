'''
Created on 2016. 1. 11.

@author: beatific J
'''

class ExceptionHandler(object):

    def handle(self, ex):
        pass

class DefaultExceptionHandler(ExceptionHandler):
    
    def handle(self, ex):
            
        print '-'*40
#         print ex
        import traceback
        traceback.print_exc()
        print '-'*40
