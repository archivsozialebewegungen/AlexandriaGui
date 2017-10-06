'''
Created on 23.10.2015

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from alexpresenters.messagebroker import CONF_EVENT_CHANGED,\
    CONF_DOCUMENT_CHANGED, REQ_SET_EVENT, Message, REQ_SAVE_CURRENT_DOCUMENT,\
    REQ_SAVE_CURRENT_EVENT

class DocumentEventReferencesPresenter:
    '''
    Handles the relations from document to events
    '''
    
    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 reference_service: baseinjectorkeys.REFERENCE_SERVICE_KEY):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.reference_service = reference_service
        self.view = None # is set on initialization
        
    def receive_message(self, message):
        if message.key == CONF_EVENT_CHANGED:
            self.view.current_event = message.event
        if message.key == CONF_DOCUMENT_CHANGED:
            self.view.current_document = message.document
            self._load_document_event_references(message.document)
            
    def _load_document_event_references(self, document):
        if document == None:
            self.view.items = []
        else:
            self.view.items = self.reference_service.get_events_referenced_by_document(document)
    
    def change_event(self):
        selected_event = self.view.selected_item
        if selected_event == None:
            return
        message = Message(REQ_SET_EVENT, event=selected_event)
        self.message_broker.send_message(message)
    
    def reference_event(self):
        if self.view.current_event is not None and self.view.current_event.id is None:
            self.message_broker.send_message(Message(REQ_SAVE_CURRENT_EVENT))
            assert(self.view.current_event.id is not None)
        reference_event = self.view.reference_event
        if reference_event == None:
            return
        if self.view.current_document.id is None:
            self.message_broker.send_message(Message(REQ_SAVE_CURRENT_DOCUMENT))
            assert(self.view.current_document.id is not None)
        self.reference_service.link_document_to_event(self.view.current_document, reference_event)
        self._load_document_event_references(self.view.current_document)
    
    def remove_event_reference(self):
        selected_event = self.view.selected_item
        if selected_event == None:
            return
        self.reference_service.delete_document_event_relation(self.view.current_document, selected_event)
        self._load_document_event_references(self.view.current_document)
