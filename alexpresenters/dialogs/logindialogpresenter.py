'''
Created on 12.03.2016

@author: michael
'''
from alexpresenters.dialogs.abstractdialogpresenter import AbstractInputDialogPresenter
from injector import inject
from alexandriabase import baseinjectorkeys

class LoginCreatorProvider(object):
    
    def __init__(self):
        self.creator = None
        

class LoginDialogPresenter(AbstractInputDialogPresenter):
    '''
    Dialog for selecting the application user
    '''

    @inject
    def __init__(self,
                 creator_service: baseinjectorkeys.CREATOR_SERVICE_KEY,
                 login_creator_provider: baseinjectorkeys.CREATOR_PROVIDER_KEY):
        '''
        Constructor
        '''
        super().__init__()
        self.creator_service = creator_service
        self.login_creator_provider = login_creator_provider
        
    def set_creators(self):
        self.view.creators = self.creator_service.find_all_active_creators()
    
    def assemble_return_value(self):
        '''
        This dialog has no return value but configures the login_creator_provider.
        It just sets the return_value to True or False to indicate, if the provider
        has been configured
        '''
        creator = self.view.input
        if creator == None:
            self.view.return_value = False
        else:
            self.login_creator_provider.creator = creator
            self.view.return_value = True