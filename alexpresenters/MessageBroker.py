'''
Created on 03.05.2015

@author: michael
'''
from injector import singleton


REQ_SET_EVENT = "set event"
REQ_SET_DOCUMENT = "set document"
REQ_SAVE_CURRENT_DOCUMENT = "save current document"
REQ_GOTO_FIRST_EVENT = "goto first event"
REQ_GOTO_FIRST_DOCUMENT = "goto first document"
REQ_SAVE_CURRENT_EVENT = "save current event"
REQ_QUIT = "quit"
REQ_SAVE_ALL = "save_all"

CONF_DOCUMENT_CHANGED = 'document changed'
CONF_EVENT_CHANGED = 'event changed'

CONF_SETUP_FINISHED = 'setup successful finished'

ERROR_MESSAGE = 'error message'

class Message:
    
    def __init__(self, key, **params):
        
        self.key = key
        for name, value in params.items():
            setattr(self, name, value)
            
    def __eq__(self, other):
        '''
        The comparison allows to compare a message directly
        to its key (makes the code more readable)
        '''
        try:
            return self.key == other.key
        except AttributeError:
            return self.key == other
        
    def __str__(self):
        return self.key

@singleton
class MessageBroker:
    
    def __init__(self):
        
        self.receivers = []
        
    def subscribe(self, receiver):
        
        self.receivers.append(receiver)
        
    def send_message(self, message):
        
        for receiver in self.receivers:
            receiver.receive_message(message)

    def show_error(self, errormessage):
        
        self.send_message(Message(ERROR_MESSAGE,
                                  messagetype='error',
                                  message=errormessage))
        
    def show_warning(self, errormessage):
        
        self.send_message(Message(ERROR_MESSAGE,
                                  messagetype='warning',
                                  message=errormessage))
        
    def show_info(self, errormessage):
        
        self.send_message(Message(ERROR_MESSAGE,
                                  messagetype='info',
                                  message=errormessage))

    def show_debug(self, errormessage):
        
        self.send_message(Message(ERROR_MESSAGE,
                                  messagetype='debug',
                                  message=errormessage))