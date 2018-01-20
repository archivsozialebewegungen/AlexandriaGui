'''
Created on 05.01.2018

@author: michael
'''
from alexpresenters.messagebroker import REQ_SET_EVENT, CONF_EVENT_CHANGED,\
    Message, REQ_SET_DOCUMENT, CONF_DOCUMENT_CHANGED, ERROR_MESSAGE,\
    MessageBroker
from WindowTestHelpers import ReferenceServiceStub, EventServiceStub,\
    DocumentServiceStub
from alexpresenters.components.references.documenteventreferencespresenter import DocumentEventReferencesPresenter
from alexpresenters.dialogs.eventselectionpresenter import EventSelectionPresenter
from tkgui.dialogs.eventselectiondialog import EventSelectionWizard
from tkgui.components.references.documenteventreferences import DocumentEventReferencesView
from tkinter.constants import TOP
from alexandriabase.domain import Document
from tkinter.ttk import Button
from alexandriabase.config import Config
from unittest.mock import MagicMock
from alexpresenters.components.references.documentfilereferencespresenter import DocumentFileReferencesPresenter
from tkgui.dialogs.fileselectiondialog import FileSelectionDialog
from tkgui.mainwindows.fileviewers import DefaultViewer
from tkgui.components.references.documentfilereference import DocumentFileReferencesView
from alexpresenters.components.references.eventcrossreferencespresenter import EventCrossReferencesPresenter
from tkgui.components.references.eventcrossreferences import EventCrossReferencesView
from manual.dialogs_test import DialogTest, DialogTestRunner

class ReferenceComponentTest(DialogTest):
    
    def __init__(self, window_manager):
        self.message_broker = MessageBroker()
        self.message_broker.subscribe(self)
        super().__init__(window_manager)
        
    def receive_message(self, message):
        if message == REQ_SET_EVENT:
            self.message_broker.send_message(Message(CONF_EVENT_CHANGED, event=message.event))
        if message == REQ_SET_DOCUMENT:
            self.message_broker.send_message(Message(CONF_DOCUMENT_CHANGED, document=message.document))
        if message == CONF_EVENT_CHANGED:
            self.message_label.set("Current event: %s" % message.event)
        if message == CONF_DOCUMENT_CHANGED:
            self.message_label.set("Current document: %s" % message.document)
        if message == ERROR_MESSAGE:
            self.message_label.set(message.message)

class ReferencesTestRunner(DialogTestRunner):
    
    def create_test_instances(self, test_classes):
        self.test_instances = []
        for test_class in test_classes:
            self.test_instances.append(test_class(self.window_manager))

class DocumentEventReferencesTest(ReferenceComponentTest):
    '''
    Test class to test the working of the widget. The systematic_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the presenter.
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Document event references"

    def create_mocks_and_stubs(self):
        self.reference_service = ReferenceServiceStub()
        self.event_service = EventServiceStub()

    def create_view(self, master):
        self.document_event_references_presenter = DocumentEventReferencesPresenter(
            self.message_broker,
            self.reference_service)
        dialog_presenter = EventSelectionPresenter(self.event_service)
        dialog_view = EventSelectionWizard(self.window_manager, dialog_presenter)
        DocumentEventReferencesView(master,
                                    self.document_event_references_presenter,
                                    dialog_view).pack(side=TOP)

    def add_button(self, master):

        message = Message(REQ_SET_DOCUMENT, document=Document(1))
        load_references_button = Button(master, text='Change document',
                                command=lambda m=message: self.message_broker.send_message(m))
        load_references_button.pack(side=TOP)

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.create_view(master)
        self.add_button(master)

class DocumentFileReferencesTest(ReferenceComponentTest):
        
    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Document file references"

    def create_mocks_and_stubs(self):
        self.document_service = DocumentServiceStub()
        self.config = MagicMock(spec=Config)
        self.config.filetypes = ['tif']
        self.config.filetypealiases = {'tif': 'TIFF'}
    
    def create_widget(self, master):
    
        presenter = DocumentFileReferencesPresenter(
            self.message_broker,
            self.document_service)
        file_selection_dialog = FileSelectionDialog(self.config)
        viewers = {'default': DefaultViewer()}
        viewers['tif'] = viewers['default']
        view = DocumentFileReferencesView(
            master,
            presenter,
            file_selection_dialog,
            viewers)
        view.pack(side=TOP)

    def add_button(self, master):
        Button(master, 
            text='Change to document 1',
            command=self.send_message).pack(side=TOP)

    def send_message(self):
        message = Message(REQ_SET_DOCUMENT, document=Document(1))
        self.message_broker.send_message(message)
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.create_widget(master)
        self.add_button(master)

class EventCrossReferencesTest(ReferenceComponentTest):
    '''
    Test class to test the working of the widget. The event_cross_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the event_cross_references_presenter.
    '''
    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Event cross references"

    def create_mocks_and_stubs(self):
        self.service = EventServiceStub()

    def create_view(self, master):
        self.event_cross_references_presenter = EventCrossReferencesPresenter(
            self.message_broker,
            self.service)
        self.event_selection_presenter = EventSelectionPresenter(
            self.service)
        self.event_selection_dialog = EventSelectionWizard(
            self.window_manager, self.event_selection_presenter)
        self.view = EventCrossReferencesView(
            master,
            self.event_cross_references_presenter,
            self.event_selection_dialog)
        self.view.pack(side=TOP)

    def add_button(self, master):
    
        load_references_button = Button(master, text='Change event',
                                command=self._change_event)
        load_references_button.pack(side=TOP)
    
    def _change_event(self):
        message = Message(CONF_EVENT_CHANGED, event=self.service.events[-1])
        self.message_broker.send_message(message)
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.create_view(master)
        self.add_button(master)
        

if __name__ == '__main__':
    test_classes = []
    test_classes.append(DocumentEventReferencesTest)
    test_classes.append(DocumentFileReferencesTest)
    test_classes.append(EventCrossReferencesTest)
    test_runner = ReferencesTestRunner(test_classes)
    test_runner.run()
