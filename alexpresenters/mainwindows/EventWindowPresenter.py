'''
Created on 20.11.2015

@author: michael
'''
from alexpresenters.mainwindows.BaseWindowPresenter import BaseWindowPresenter
from injector import inject
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from alexpresenters.messagebroker import Message, CONF_EVENT_CHANGED,\
    REQ_SET_EVENT, CONF_EVENT_WINDOW_READY, REQ_GOTO_FIRST_EVENT,\
    REQ_SAVE_CURRENT_EVENT

class EventWindowPresenter(BaseWindowPresenter):
    
    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY,
            event_service=baseinjectorkeys.EventServiceKey,
            post_processors=guiinjectorkeys.EVENT_WINDOW_POST_PROCESSORS_KEY)
    def __init__(self, message_broker, event_service, post_processors):
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

    def create_new(self):
        self._save_if_necessary()
        date_range = self.view.new_date_range
        if date_range == None:
            return
        selected_event = self.view.existing_new_event
        if selected_event is not None:
            self._change_entity(selected_event)
        else:
            self._change_entity(self.entity_service.create_new(date_range))

    def goto_record(self):
        # TODO: This conversion should be moved to the dao
        event_date = self.view.record_id_selection
        if event_date == None:
            return
        new_entity = self.entity_service.get_nearest(event_date, self.view.filter_expression)
        self._change_entity(new_entity)

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
            
    def signal_window_ready(self):
        self.message_broker.send_message(Message(CONF_EVENT_WINDOW_READY))