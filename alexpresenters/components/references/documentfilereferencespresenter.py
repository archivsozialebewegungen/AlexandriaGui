'''
Created on 30.01.2016

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from alexpresenters.messagebroker import CONF_DOCUMENT_CHANGED, Message, \
    ERROR_MESSAGE, REQ_SAVE_CURRENT_DOCUMENT
from alexandriabase.services.fileformatservice import UnsupportedFileFormat, \
    UnsupportedFileResolution

from alexandriabase.services.documentfilemanager import DocumentFileNotFound

class DocumentFileReferencesPresenter():
    '''
    Handles the relations from document to document files
    '''
    
    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY,
            document_service=baseinjectorkeys.DocumentServiceKey)
    def __init__(self, message_broker, document_service):
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
            
    
