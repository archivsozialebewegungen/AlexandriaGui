'''
Created on 22.10.2015

@author: michael
'''
from injector import inject
from alexandriabase import baseinjectorkeys

class EventConfirmationPresenter:
    '''
    Presenter for the event selection wizard
    '''    
    @inject(event_service=baseinjectorkeys.EventServiceKey)
    def __init__(self, event_service):
        self.event_service = event_service
    
    def set_event_list(self):
        '''
        Selects the events into the view
        '''
        self.view.event_list = self.event_service.get_events_for_date(self.view.date)
