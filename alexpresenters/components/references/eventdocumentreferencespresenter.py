'''
Created on 23.10.2015

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from alexpresenters.messagebroker import CONF_EVENT_CHANGED,\
    CONF_DOCUMENT_CHANGED, Message, REQ_SET_DOCUMENT, ERROR_MESSAGE,\
    REQ_SAVE_CURRENT_EVENT, REQ_SAVE_CURRENT_DOCUMENT
from alexandriabase.base_exceptions import NoSuchEntityException

class EventDocumentReferencesPresenter:
    '''
    Handles the relations from document to events
    '''
    
    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 document_service: baseinjectorkeys.DOCUMENT_SERVICE_KEY,
                 reference_service: baseinjectorkeys.REFERENCE_SERVICE_KEY):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.document_service = document_service
        self.reference_service = reference_service
        self.view = None # is set on initialization
        
    def receive_message(self, message):
        if message.key == CONF_EVENT_CHANGED:
            self.view.current_event = message.event
            self._load_event_document_references(message.event)
        if message.key == CONF_DOCUMENT_CHANGED:
            self.view.current_document = message.document
            
    def _load_event_document_references(self, event):
        if event == None:
            self.view.items = []
        else:
            self.view.items = self.reference_service.get_documents_referenced_by_event(event)
    
    def change_document(self):
        selected_document = self.view.selected_item
        if selected_document == None:
            return
        message = Message(REQ_SET_DOCUMENT, document=selected_document)
        self.message_broker.send_message(message)
    
    def reference_document(self):
        if self.view.current_document is not None and self.view.current_document.id is None:
            self.message_broker.send_message(Message(REQ_SAVE_CURRENT_DOCUMENT))
            assert(not self.view.current_document.id is None)
            
        documentid = self.view.new_documentid
        if documentid == None:
            return
        try:
            document = self.document_service.get_by_id(documentid)
        except NoSuchEntityException:
            self.message_broker.send_message(Message(ERROR_MESSAGE, 
                                                     messagetype='error', 
                                                     message='No such document'))
            return
        if self.view.current_event.id is None:
            self.message_broker.send_message(Message(REQ_SAVE_CURRENT_EVENT))
            assert(not self.view.current_event.id is None)
        self.reference_service.link_document_to_event(document, self.view.current_event)
        self._load_event_document_references(self.view.current_event)
    
    def remove_document_reference(self):
        selected_document = self.view.selected_item
        if selected_document == None:
            return
        self.reference_service.delete_document_event_relation(selected_document, self.view.current_event)
        self._load_event_document_references(self.view.current_event)
