'''
Created on 23.10.2015

@author: michael
'''
class GenericTreeSelectionPresenter:
    
    def __init__(self):
        self.view = None

    def assemble_return_value(self):
        self.view.return_value = self.view.input.entity