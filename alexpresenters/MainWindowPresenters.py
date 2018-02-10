'''
Created on 07.02.2018

@author: michael
'''
from injector import inject
from alexandriabase import baseinjectorkeys
from alexpresenters.MessageBroker import Message, REQ_QUIT,\
    CONF_DOCUMENT_CHANGED, REQ_SAVE_CURRENT_DOCUMENT, REQ_SET_DOCUMENT,\
    REQ_GOTO_FIRST_DOCUMENT, CONF_EVENT_CHANGED, REQ_SAVE_CURRENT_EVENT,\
    REQ_SET_EVENT, REQ_GOTO_FIRST_EVENT
from tkgui import guiinjectorkeys
import re

class BaseWindowPresenter:
    
    def __init__(self, message_broker, entity_service, post_processors):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.entity_service = entity_service
        self.post_processors = post_processors
        self.filter_expression = None
        self.view = None # Will be set by view

    def goto_first(self):
        self._change_entity(self.entity_service.get_first(self.filter_expression))
    
    def goto_next(self):
        entity = self._save_if_necessary()
        if entity == None or entity.id == None:
            return
        self._change_entity(self.entity_service.get_next(entity, self.filter_expression))

    def goto_previous(self):
        entity = self._save_if_necessary()
        if entity == None or entity.id == None:
            return
        self._change_entity(self.entity_service.get_previous(entity, self.filter_expression))

    def goto_last(self):
        self._change_entity(self.entity_service.get_last(self.filter_expression))
        
    def goto_record(self):
        if self.view.new_record_id == None:
            return
        new_entity = self.entity_service.get_nearest(self.view.new_record_id,
                                                     self.filter_expression)
        self._change_entity(new_entity)
        
    def update_filter_expression(self):
        if self.view.filter_object is not None:
            self.filter_expression = self.entity_service.create_filter_expression(self.view.filter_object)
        else:
            self.filter_expression = None
        
    def create_new(self):
        self._change_entity(self.entity_service.create_new())
    
    def delete(self):
        entity = self.view.entity
        # Quite a lot of ugly edge cases - should be handled by the gui - but you never know
        if entity == None:
            # No entity displayed at all
            return
        if entity.id == None:
            # Entity is not yet saved, so we just jump to the last entity
            self.view.entity = self.entity_service.get_last(self.filter_expression)
            return
        
        first_entity = self.entity_service.get_first(self.filter_expression)
        if first_entity == self.view.entity:
            goto_entity = self.entity_service.get_next(entity, self.filter_expression)
        else:
            goto_entity = self.entity_service.get_previous(entity, self.filter_expression)
        self.entity_service.delete(entity)
        if goto_entity == entity:
            # We just deleted the last entity
            self._change_entity(None)
        else:
            self._change_entity(goto_entity)

    def quit(self):
        self.message_broker.send_message(Message(REQ_QUIT))
    
    def _change_entity(self, entity):
        self._save_if_necessary()
        self.view.entity = entity
    
    def _save(self):
        entity = self.view.entity
        if not entity.id:
            entity = self.entity_service.save(entity) # Post processors may need an id
        for post_processor in self.post_processors:
            entity = post_processor.run(entity)
        entity = self.entity_service.save(entity)
        return entity
    
    def _save_if_necessary(self):
        has_changed = self.view.entity_has_changed()
        if has_changed:
            return self._save()
        else:
            return self.view.entity
        
class DocumentWindowPresenter(BaseWindowPresenter):
    '''
    The presenter class for the document window
    '''

    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 document_service: baseinjectorkeys.DOCUMENT_SERVICE_KEY,
                 post_processors: guiinjectorkeys.DOCUMENT_WINDOW_POST_PROCESSORS_KEY):
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
class DocumentTypePostProcessor(object):

    @inject
    def __init__(self, document_type_service: baseinjectorkeys.DOCUMENT_TYPE_SERVICE_KEY):
        self.type_dict = document_type_service.get_document_type_dict()
        self.doctype_re = self.build_doctype_re()
        
    def build_doctype_re(self):
        pattern = r"^\s*(%s)\s*:\s*(.*)" % '|'.join(self.type_dict.keys())
        return re.compile(pattern, re.IGNORECASE)
    
    def run(self, entity):
        
        matcher = self.doctype_re.match(entity.description)
        if matcher:
            entity.description = matcher.group(2)
            entity.document_type = self.type_dict[matcher.group(1).upper()]
        return entity

class JournalDocTypePostProcessor(object):

    @inject
    def __init__(self, document_type_service: baseinjectorkeys.DOCUMENT_TYPE_SERVICE_KEY):
        self.doc_type = document_type_service.get_by_id(13)
        month_pattern = r"\s*(\d{1,2}\.|Januar|Februar|März|April|Mai|" +\
            r"Juni|Juli|August|September|Oktober|November|Dezember|" +\
            r"Jan\.|Feb\.|Mär\.|Apr\.|Mai|Jun\.|Jul\.|Aug\.|Sep\.|Oct\.|Nov\.|Dez\.)\s*"
        delimiter_pattern = r"(vom|,)\s+"
        self.doctype_re = re.compile(r"^(.{1,30}?" + 
                                     delimiter_pattern + 
                                     r"\d+\." + 
                                     month_pattern 
                                     + r"\d+)", 
                                     re.IGNORECASE)
        
    def run(self, entity):
        
        if entity.document_type != None and entity.document_type.id != 1:
            return entity
        
        matcher = self.doctype_re.match(entity.description)
        if matcher:
            entity.document_type = self.doc_type
        return entity
