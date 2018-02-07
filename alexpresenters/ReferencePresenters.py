'''
Created on 22.01.2018

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from alexpresenters import _
from alexpresenters.MessageBroker import CONF_EVENT_CHANGED, Message,\
    REQ_SAVE_CURRENT_EVENT, REQ_SAVE_CURRENT_DOCUMENT, CONF_DOCUMENT_CHANGED,\
    REQ_SET_EVENT, ERROR_MESSAGE, REQ_SET_DOCUMENT
from alexandriabase.services import DocumentFileNotFound, UnsupportedFileFormat,\
    UnsupportedFileResolution
from alexandriabase.base_exceptions import NoSuchEntityException

class EventTypeReferencesPresenter:
    '''
    Handles the relations from document to events
    '''
    
    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 event_service: baseinjectorkeys.EVENT_SERVICE_KEY):
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

class DocumentFileReferencesPresenter():
    '''
    Handles the relations from document to document files
    '''
    
    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 document_service: baseinjectorkeys.DOCUMENT_SERVICE_KEY):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.document_service = document_service
        self.view = None  # is set on initialization

    def receive_message(self, message):
        if message == CONF_DOCUMENT_CHANGED:
            self.view.current_document = message.document
            self._load_file_infos(message.document)
            
    def _load_file_infos(self, document):
        if document == None:
            self.view.items = []
        else:
            self.view.items = self.document_service.get_file_infos_for_document(document)
            
    def add_file(self):
        file = self.view.new_file
        if file == None or self.view.current_document == None:
            return
        if self.view.current_document.id is None:
            self.message_broker.send_message(Message(REQ_SAVE_CURRENT_DOCUMENT))
            assert(self.view.current_document.id is not None)
        if self._execute_with_errorhandling(self.document_service.add_document_file,
                                             self.view.current_document,
                                             file):
            self._load_file_infos(self.view.current_document)
    
    def replace_file(self):
        file_info = self.view.selected_item
        if not file_info:
            return
        file = self.view.new_file
        if not file:
            return
        if self._execute_with_errorhandling(self.document_service.replace_document_file,
                                             file_info,
                                             file):
            self._load_file_infos(self.view.current_document)
        
    def _execute_with_errorhandling(self, method, *params):     
        try:
            method(*params)
        except UnsupportedFileFormat as e:
            message = Message(
                ERROR_MESSAGE,
                messagetype='error',
                message=_("File format '%s' is not supported!" % e.file_format)
            )
            self.message_broker.send_message(message)
            return False
        except UnsupportedFileResolution as e:
            message = Message(
                ERROR_MESSAGE,
                messagetype='error',
                message=_("File resolution {0:d} x {1:d} is not supported!".format(
                    int(e.x_resolution),
                    int(e.y_resolution))
                )
            )
            self.message_broker.send_message(message)
            return False
        except Exception as e:
            try:
                message_text = e.strerror
            except AttributeError:
                message_text = _("Unknown error while adding file")
            message = Message(
                ERROR_MESSAGE,
                messagetype='error',
                message=message_text
            )
            self.message_broker.send_message(message)
            return False
        return True

    def show_file(self):
        if not self.view.selected_item:
            return 
        try:
            self.view.show_file = self.document_service.get_file_for_file_info(self.view.selected_item)
        except DocumentFileNotFound as exception:
            self.message_broker.send_message(
                Message(ERROR_MESSAGE,
                        message=_("Document %s not found" % exception.document_file_info),
                        messagetype='error'))
    
    def remove_file(self):
        file_info = self.view.selected_item
        if not file_info:
            return
        self.document_service.delete_file(file_info)
        self._load_file_infos(self.view.current_document)
            
    
class EventCrossReferencesPresenter:

    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 event_service: baseinjectorkeys.EVENT_SERVICE_KEY):
        self.message_broker = message_broker
        self.message_broker.subscribe(self)
        self.event_service = event_service
        self.view = None # is set on initialization
        
    def receive_message(self, message):
        if message.key == CONF_EVENT_CHANGED:
            self._load_event_crossreferences(message)
    
    def _load_event_crossreferences(self, message):
        self.view.current_event = message.event
        self._update_crossreferences()
    
    def _update_crossreferences(self):
        self.view.items = self.event_service.get_cross_references(self.view.current_event)
       
    def goto_event(self):
        selected_event = self.view.selected_item
        if not selected_event:
            return
        message = Message(REQ_SET_EVENT, event=selected_event)
        self.message_broker.send_message(message)
    
    def add_new_cross_reference(self):
        new_cross_reference_event = self.view.new_cross_reference_event
        if new_cross_reference_event != None:
            if self.view.current_event.id is None:
                self.message_broker.send_message(Message(REQ_SAVE_CURRENT_EVENT))
            assert(not self.view.current_event.id is None)
            self.event_service.add_cross_reference(self.view.current_event, new_cross_reference_event)
        self._update_crossreferences()
    
    def delete_cross_reference(self):
        selected_event = self.view.selected_item
        if not selected_event:
            return
        self.event_service.remove_cross_reference(self.view.current_event, selected_event)
        self._update_crossreferences()
        
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
            
        document_id = self.view.new_document_id
        if document_id == None:
            return
        try:
            document = self.document_service.get_by_id(document_id)
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
