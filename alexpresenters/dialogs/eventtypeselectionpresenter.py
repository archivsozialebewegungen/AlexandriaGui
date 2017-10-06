'''
Created on 23.10.2015

@author: michael
'''
from alexandriabase import baseinjectorkeys
from injector import inject
from alexpresenters.dialogs.generic_tree_selection_presenter import GenericTreeSelectionPresenter

class EventTypeSelectionPresenter(GenericTreeSelectionPresenter):
    
    @inject
    def __init__(self, event_service: baseinjectorkeys.EVENT_SERVICE_KEY):
        super().__init__()
        self.event_service = event_service
        
    def get_tree(self):
        self.view.tree = self.event_service.get_event_type_tree()
