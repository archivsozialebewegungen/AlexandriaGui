'''
Created on 20.11.2015

@author: michael
'''
from alexpresenters.mainwindows.BaseWindowPresenter import BaseWindowPresenter
from injector import inject
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from alexpresenters.messagebroker import Message, CONF_EVENT_CHANGED,\
    REQ_SET_EVENT, REQ_GOTO_FIRST_EVENT, REQ_SAVE_CURRENT_EVENT

class EventWindowPresenter(BaseWindowPresenter):
    
    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 event_service: baseinjectorkeys.EVENT_SERVICE_KEY,
                 post_processors: guiinjectorkeys.EVENT_WINDOW_POST_PROCESSORS_KEY):
        super().__init__(message_broker, event_service, post_processors)
    '''
    classdocs
    '''
    def change_event_date(self):
        date_range = self.view.new_date_range
        if date_range == None:
            return
        self.view.entity.daterange = date_range
        self.entity_service.save(self.view.entity)

    def fetch_events_for_new_event_date(self):
        
        self.view.event_list = self.entity_service.get_events_for_date(
            self.view.date_range_for_new_event.start_date)

    def create_new(self):
        
        self._change_entity(self.entity_service.create_new(self.view.date_range_for_new_event))

    def _change_entity(self, entity):
        BaseWindowPresenter._change_entity(self, entity)
        self.message_broker.send_message(Message(CONF_EVENT_CHANGED, event=entity))
    
    def receive_message(self, message):
        if message == REQ_SAVE_CURRENT_EVENT:
            entity = self._save()
            self.message_broker.send_message(Message(CONF_EVENT_CHANGED, event=entity))
        if message == REQ_SET_EVENT:
            self._change_entity(message.event)
        if message == REQ_GOTO_FIRST_EVENT:
            self.goto_first()
            