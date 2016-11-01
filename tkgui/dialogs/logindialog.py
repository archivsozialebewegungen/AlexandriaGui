'''
Created on 12.03.2016

@author: michael
'''
from tkgui.dialogs.abstractdialog import AbstractInputDialog
from tkgui import guiinjectorkeys
from injector import inject
from tkgui.components.alexwidgets import AlexComboBoxDialog

class LoginDialog(AbstractInputDialog):
    '''
    classdocs
    '''

    @inject(presenter=guiinjectorkeys.LOGIN_DIALOG_PRESENTER_KEY)
    def __init__(self, presenter):
        '''
        Constructor
        '''
        super().__init__(presenter)
        self.creators = []
        self.presenter.set_creators()
        
    def _init_dialog(self, master):
        self.dialog = AlexComboBoxDialog(master,
            title = _('User selection dialog'),
            buttons = (_('OK'), _('Cancel')),
            defaultbutton = _('OK'),
            combobox_labelpos = 'n',
            label_text = _('Please select user'),
            scrolledlist_items = self.creators)
        self.dialog.withdraw()
        
    input = property(lambda self: self.dialog.get())
