'''
Created on 20.11.2015

@author: michael
'''
from tkinter.constants import END
from tkinter import Entry, Label, Frame
import os
from alex_test_utils import get_testfiles_dir
from alexandriabase.domain import Entity, Event, Document,\
    AlexDateRange, DocumentFileInfo, EventType, Tree, EventTypeIdentifier
from alexandriabase.services import FileFormatService
from alexandriabase.config import Config
from tkgui.MainWindows import BaseWindow


class StringDialogStub:
        
    def __init__(self):
        self.label = 'Enter string value:'
        self.dialog = None
        
    def activate(self, master):
        # pylint: disable=no-member
        self.dialog = Pmw.PromptDialog(master,  # @UndefinedVariable
                                       title='Entry',
                                       label_text=self.label,
                                       entryfield_labelpos='n',
                                       defaultbutton=0,
                                       buttons=('OK', 'Cancel'),
                                       command=self.execute)
        self.dialog.activate()
        return self.return_value
            
    def execute(self, result):
        if result is None or result == 'Cancel':
            self.return_value = None
        else:
            self.return_value = self.dialog.get()
        self.dialog.deactivate()
            
class IntDialogStub(StringDialogStub):
        
    def __init__(self):
        self.label = 'Enter integer value:'
        
    def execute(self, result):
            
        super().execute(result)
        try:
            self.return_value = int(self.return_value)
        except:
            self.return_value = None
        return self.return_value
                       
class ReferenceStub:
        
    def get_view(self, parent):
        frame = Frame(parent);
        Label(frame, text="A reference widget").pack()
        return frame
    
class EntityStub(Entity):
        
    def __init__(self, entity_id=None):
        super().__init__(entity_id)
        self._text = ''
        
    def _set_text(self, text):
        self._text = text
        
    def _get_text(self):
        return self._text
        
    text = property(_get_text, _set_text)
             
class BaseWindowStub(BaseWindow):
        
    def entity_has_changed(self):
        if self.entity == None:
            return False
        return self.entity.text != self.entry.get() or self.entity.id == None 
        
    def _populate_entity_frame(self):
        self.entry = Entry(self.entity_frame, text="")
        self.entry.pack()
            
    def _entity_to_view(self, entity):
        self._entity = entity
        self.entry.delete(0, END)
        if entity != None:
            self.entry.insert(END, entity.text)
            
    def _view_to_entity(self):
        if self._entity != None:
            self._entity.text = self.entry.get()
        return self._entity
    
class EntityServiceStub:
        
    def __init__(self):
        self.entities = []
            
    def get_by_id(self, entity_id):
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None
            
    def get_first(self, filter_expression):
        if len(self.entities) == 0:
            return None
        return self.entities[0]
        
    def get_next(self, entity, filter_expression):
        try:
            index = self.entities.index(entity)
        except:
            return self.get_last(filter_expression)
        if index == len(self.entities) - 1:
            return self.get_first(filter_expression)
        return self.entities[index + 1]
                
    def get_previous(self, entity, filter_expression):
        try:
            index = self.entities.index(entity)
        except:
            return self.get_first(filter_expression)
        if index == 0:
            return self.get_last(filter_expression)
        return self.entities[index - 1]

    def get_last(self, filter_expression):
        if len(self.entities) == 0:
            return None
        return self.entities[-1]
        
    def create_new(self):
        entity = EntityStub()
            
        if len(self.entities) == 0:
            entity.text = "New Entity 0"
        else:
            entity.text = "New Entity %d" % (self.entities[-1].id + 1)
        return entity
        
    def delete(self, entity):
        index = self.entities.index(entity)
        self.entities[index:index + 1] = []
            
    def save(self, entity):
        if entity.id == None:
            if len(self.entities) == 0:
                entity._id = 0
            else:
                entity._id = self.entities[-1].id + 1
            self.entities.append(entity)
        return entity
        
    def create_filter_expression(self, filter_object):
        # pylint: disable=no-member
        Pmw.MessageDialog(None,  # @UndefinedVariable
                          defaultbutton=0,
                          message_text='This would start filtering!').activate() # @UndefinedVariable
        return filter_object
            
class EventServiceStub(EntityServiceStub):            

    def __init__(self):
        self.events = []
        self.events.append(Event(1940010101))
        self.events[-1].daterange = AlexDateRange(1940010100, None)
        self.events[-1].description = "Demo event 1"
        self.crossreferences = {}
        self.crossreferences[self.events[-1]] = []

    def create_new(self, date_range):
        event = Event()
        event.daterange = date_range
        return event
            
    def get_events_for_date(self, alex_date):
        '''
        This just invents some events and adds it to our "database"
        '''
        events = []
        for counter in range(1,3):
            event = Event(alex_date.as_key(counter))
            event.daterange = AlexDateRange(alex_date.as_key(counter), None)
            event.description = "Demo event %d" % counter
            events.append(event)
            self.events.append(event)
        return events
                
    def get_cross_references(self, event):
        return self.crossreferences[event]
        
    def add_cross_reference(self, event1, event2):
        if not event1 in self.crossreferences:
            self.crossreferences[event1] = [] 
        if not event2 in self.crossreferences:
            self.crossreferences[event2] = [] 
        self.crossreferences[event1].append(event2)
        self.crossreferences[event2].append(event1)
        
    def remove_cross_reference(self, event1, event2):
        self.crossreferences[event1] = [x for x in self.crossreferences[event1] if x != event2]
        self.crossreferences[event2] = [x for x in self.crossreferences[event2] if x != event1]
    
    def get_event_type_tree(self):
        
        event_types = (EventType(EventTypeIdentifier(0,0), "root"),
                       EventType(EventTypeIdentifier(1,0), "parent1"),
                       EventType(EventTypeIdentifier(1,1), "child11"),
                       EventType(EventTypeIdentifier(1,2), "child12"),
                       EventType(EventTypeIdentifier(2,0), "parent2"),
                       EventType(EventTypeIdentifier(2,1), "child21"),
                       EventType(EventTypeIdentifier(2,2), "child22"),
                       )
        
        return Tree(event_types)

class DocumentServiceStub(EntityServiceStub):            

    def __init__(self):
        config = Config(os.path.join(get_testfiles_dir(), "testconfig.xml"))
        self.file_format_service = FileFormatService(config)
        self.file_infos = {}
        document = Document(1)
        self.file_infos[document] = []
        file_info = DocumentFileInfo(1)
        file_info.document_id = 1
        file_info.filetype = "tif"
        file_info.resolution = 300
        self.file_infos[document].append(file_info)

    def create_new(self):
        document = Document()
        return document

    def get_file_infos_for_document(self, document):
        return self.file_infos[document]
        
    def add_document_file(self, document, file):
        file_info = DocumentFileInfo(len(self.file_infos[document]) + 1)
        filetype, res = self.file_format_service.get_format_and_resolution(file)
        file_info.filetype = filetype
        file_info.resolution = res
        file_info.document_id = document.id
        self.file_infos[document].append(file_info)
        
    def delete_file(self, file_info):
        for document in self.file_infos:
            if document.id == file_info.document_id:
                self.file_infos[document] = [fi for fi in self.file_infos[document] if fi.id != file_info.id]
                
    def replace_document_file(self, file_info, file):
        file_info.filetype, file_info.resolution = self.file_format_service.get_format_and_resolution(file)
        
    def get_file_for_file_info(self, file_info):
        return os.path.join(get_testfiles_dir(), "testfile.jpg")
        

class ReferenceServiceStub:
        
    def __init__(self):
        event1 = Event(1940000001)
        event1.daterange = AlexDateRange(1940000001, None)
        self.events = {}
        self.events[1] = [event1]
                
    def get_events_referenced_by_document(self, document):
        return self.events[document.id]
                       
    def link_document_to_event(self, document, event):
        self.events[document.id].append(event)

    def delete_document_event_relation(self, document, event):
        event_list = self.events[document.id]
        self.events[document.id] = [e for e in event_list if e.id != event.id]
