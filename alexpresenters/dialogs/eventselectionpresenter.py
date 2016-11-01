'''
Created on 22.10.2015

@author: michael
'''
from injector import inject
from alexandriabase import baseinjectorkeys

class EventSelectionPresenter:
    '''
    Presenter for the event selection wizard
    '''    
    @inject(event_service=baseinjectorkeys.EventServiceKey)
    def __init__(self, event_service):
        self.event_service = event_service
        self.exclude_list = []
    
    def _get_events_for_date(self, date):
        '''
        Helper method to fetch events from service an clean up
        the resulting list. The events not wanted must be included
        in the exclude_list property of the class.
        '''
        raw_list = self.event_service.get_events_for_date(date)
        clean_list = []
        for event in raw_list:
            if event in self.exclude_list:
                continue
            clean_list.append(event)
        return clean_list
    
    def update_event_list(self):
        '''
        Sets the eventlist on the second page of the wizard.
        '''
        selected_date = self.view.date
        if not selected_date:
            self.view.event_list = []
        else:
            self.view.event_list = self._get_events_for_date(selected_date)
            
    def close(self):
        '''
        Closes the wizard.
        '''
        self.view.close()
        
