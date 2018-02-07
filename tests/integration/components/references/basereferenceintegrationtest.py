'''
Created on 01.12.2016

@author: michael
'''
from integration.baseintegrationtest import BaseIntegrationTest
from alexandriabase.domain import Event, AlexDateRange, AlexDate, Document,\
    DocumentType
from alexpresenters.MessageBroker import REQ_SAVE_CURRENT_EVENT,\
    REQ_SAVE_CURRENT_DOCUMENT, Message, CONF_DOCUMENT_CHANGED,\
    CONF_EVENT_CHANGED
from alexandriabase import baseinjectorkeys
from alex_test_utils import MODE_SIMPLE

class BaseReferenceIntegrationTest(BaseIntegrationTest):
    '''
    Add some helper methods to make testing references
    more easy.
    '''
    
    def receive_message(self, message):
        BaseIntegrationTest.receive_message(self, message)
        if message == REQ_SAVE_CURRENT_EVENT:
            self.injector.get(baseinjectorkeys.EVENT_DAO_KEY).save(self.presenter.view.current_event)
        if message == REQ_SAVE_CURRENT_DOCUMENT:
            self.injector.get(baseinjectorkeys.DOCUMENT_DAO_KEY).save(self.presenter.view.current_document)

    def set_current_document(self, document_id):

        if document_id is not None:
            document = self.document_dao.get_by_id(document_id)
        else:
            document = Document()
            document.document_type = DocumentType(1)
        message = Message(CONF_DOCUMENT_CHANGED, document=document)
        
        self.message_broker.send_message(message)

    def set_current_event(self, event_id):

        if event_id is not None:
            event = self.event_dao.get_by_id(event_id)
        else:
            event = Event()
            event.daterange = AlexDateRange(AlexDate(1936), None)
        message = Message(CONF_EVENT_CHANGED, event=event)
        
        self.message_broker.send_message(message)
