'''
Created on 31.10.2015

@author: michael
'''

class AbstractInputDialogPresenter(object):
    '''
    Class that defines the expected minimal interface of a dialog
    presenter
    '''

    def __init__(self):
        self.view = None
        
    def assemble_return_value(self):
        '''
        This method should set the the return_value property
        of the view, which then will be returned to the caller of the dialog.
        It has to be overridden in the classes derived from this.
        '''
        raise NotImplementedError
        