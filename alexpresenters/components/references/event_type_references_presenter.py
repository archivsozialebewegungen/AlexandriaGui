'''
Created on 23.10.2015

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from alexpresenters.messagebroker import CONF_EVENT_CHANGED,\
    CONF_DOCUMENT_CHANGED, REQ_SET_EVENT, Message, REQ_SAVE_CURRENT_EVENT

class EventTypeReferencesPresenter:
    '''
    Handles the relations from document to events
    '''
    
    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY,
            event_service=baseinjectorkeys.EventServiceKey)
    def __init__(self, message_broker, event_service):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.event_service = event_service
        self.view = None # is set on initialization
        
    def receive_message(self, message):
        if message.key == CONF_EVENT_CHANGED:
            self.view.current_event = message.event
            self._load_event_types(message.event)
            
    def _load_event_types(self, event):
        if event == None:
            self.view.items = []
        else:
            self.view.items = self.event_service.get_event_types(event)
    
    def add_event_type_reference(self):
        new_event_type = self.view.new_event_type
        if new_event_type is None or new_event_type in self.view.items:
            return
        if self.view.current_event.id is None:
            self.message_broker.send_message(Message(REQ_SAVE_CURRENT_EVENT))
        assert(not self.view.current_event.id is None)
        self.event_service.add_event_type(self.view.current_event, new_event_type)
        self._load_event_types(self.view.current_event)
    
    def remove_event_type_reference(self):
        selected_event_type = self.view.selected_item
        if selected_event_type == None:
            return
        self.event_service.remove_event_type(self.view.current_event, selected_event_type)
        self._load_event_types(self.view.current_event)
