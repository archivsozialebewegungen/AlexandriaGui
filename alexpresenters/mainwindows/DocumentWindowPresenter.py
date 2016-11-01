'''
Created on 02.12.2015

@author: michael
'''
from alexpresenters.mainwindows.BaseWindowPresenter import BaseWindowPresenter
from alexandriabase import baseinjectorkeys
from tkgui import guiinjectorkeys
from injector import inject
from alexpresenters.messagebroker import Message, CONF_DOCUMENT_CHANGED,\
    REQ_SET_DOCUMENT, CONF_DOCUMENT_WINDOW_READY, REQ_GOTO_FIRST_DOCUMENT,\
    REQ_SAVE_CURRENT_DOCUMENT

class DocumentWindowPresenter(BaseWindowPresenter):
    '''
    The presenter class for the document window
    '''

    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY,
            document_service=baseinjectorkeys.DocumentServiceKey,
            post_processors=guiinjectorkeys.DOCUMENT_WINDOW_POST_PROCESSORS_KEY)
    def __init__(self, message_broker, document_service, post_processors):
        '''
        Constructor
        '''
        super().__init__(message_broker, document_service, post_processors)
        
    def _change_entity(self, entity):
        BaseWindowPresenter._change_entity(self, entity)
        self.message_broker.send_message(Message(CONF_DOCUMENT_CHANGED, document=entity))
        
    def receive_message(self, message):
        if message == REQ_SAVE_CURRENT_DOCUMENT:
            entity = self._save()
            self.view.entity = entity
            self.message_broker.send_message(Message(CONF_DOCUMENT_CHANGED, document=entity))
        if message == REQ_SET_DOCUMENT:
            self._change_entity(message.document)
        if message == REQ_GOTO_FIRST_DOCUMENT:
            self.goto_first()
           
    def signal_window_ready(self):
        self.message_broker.send_message(Message(CONF_DOCUMENT_WINDOW_READY))