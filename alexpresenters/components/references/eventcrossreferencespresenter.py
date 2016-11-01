'''
Created on 23.10.2015

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys

from alexandriabase import baseinjectorkeys
from alexpresenters.messagebroker import CONF_EVENT_CHANGED, REQ_SET_EVENT,\
    Message, REQ_SAVE_CURRENT_EVENT

class EventCrossReferencesPresenter:

    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY,
            event_service=baseinjectorkeys.EventServiceKey)
    def __init__(self, message_broker, event_service):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.event_service = event_service
        self.view = None # is set on initialization
        
    def receive_message(self, message):
        if message.key == CONF_EVENT_CHANGED:
            self._load_event_crossreferences(message)
    
    def _load_event_crossreferences(self, message):
        self.view.event = message.event
        self._update_crossreferences()
    
    def _update_crossreferences(self):
        self.view.items = self.event_service.get_cross_references(self.view.event)
       
    def goto_event(self):
        selected_event = self.view.selected_item
        if not selected_event:
            return
        message = Message(REQ_SET_EVENT, event=selected_event)
        self.message_broker.send_message(message)
    
    def add_new_cross_reference(self):
        new_cross_reference_event = self.view.new_cross_reference_event
        if new_cross_reference_event != None:
            if self.view.event.id is None:
                self.message_broker.send_message(Message(REQ_SAVE_CURRENT_EVENT))
            assert(not self.view.event.id is None)
            self.event_service.add_cross_reference(self.view.event, new_cross_reference_event)
        self._update_crossreferences()
    
    def delete_cross_reference(self):
        selected_event = self.view.selected_item
        if not selected_event:
            return
        self.event_service.remove_cross_reference(self.view.event, selected_event)
        self._update_crossreferences()