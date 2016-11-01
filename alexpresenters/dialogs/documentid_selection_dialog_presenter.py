'''
Created on 06.01.2016

@author: michael
'''
from alexpresenters.dialogs.abstractdialogpresenter import AbstractInputDialogPresenter

class DocumentIdSelectionDialogPresenter(AbstractInputDialogPresenter):
    '''
    A simple presenter for an integer input
    '''

    def assemble_return_value(self):
        id_as_string = self.view.input
        try:
            self.view.return_value = int(id_as_string)
        except ValueError:
            self.view.return_value = None