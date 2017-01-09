'''
Created on 22.01.2016

@author: michael
'''
from tkinter import Button
from tkgui.dialogs.eventselectiondialog import EventSelectionDialog
from alexpresenters.dialogs.eventselectionpresenter import EventSelectionPresenter
from WindowTestHelpers import EventServiceStub, ReferenceServiceStub, DocumentServiceStub
from tkinter.constants import TOP, BOTH, TRUE
from alexpresenters.messagebroker import Message,\
    CONF_EVENT_CHANGED, REQ_SET_DOCUMENT, ERROR_MESSAGE
from alexpresenters.components.references.documenteventreferencespresenter\
    import DocumentEventReferencesPresenter
from tkgui.components.references.documenteventreferences import DocumentEventReferencesView
from alexandriabase.domain import Document, InvalidDateException, Creator,\
    DocumentFileInfo
from tkgui.components.references.eventcrossreferences import EventCrossReferencesView
from tkgui.components.alexwidgets import AlexLabel, AlexDateEntry,\
    AlexMessageBar
import Pmw
from alexpresenters.components.references.documentfilereferencespresenter import \
    DocumentFileReferencesPresenter
from tkgui.components.references.documentfilereference import DocumentFileReferencesView
from tkgui.dialogs.fileselectiondialog import FileSelectionDialog
from alexandriabase.services.creatorservice import CreatorService
from unittest.mock import MagicMock
from alexpresenters.dialogs.logindialogpresenter import LoginDialogPresenter,\
    LoginCreatorProvider
from tkgui.dialogs.logindialog import LoginDialog
from alexandriabase.config import Config
from tkgui.mainwindows.BaseWindow import WindowManager
from alexandriabase.services.documentfilemanager import DocumentFileManager
from alex_test_utils import get_testfiles_dir
import os
from tkgui.mainwindows.fileviewers import ExternalViewer, DefaultViewer,\
    GraphicsViewer
from tkgui.dialogs.filterdialogs import GenericFilterDialog,\
    DocumentFilterDialog, EventFilterDialog
from alexpresenters.dialogs.filterpresenters import GenericFilterDialogPresenter,\
    DocumentFilterDialogPresenter, EventFilterDialogPresenter
from _functools import reduce
from tkgui.dialogs.GenericInputDialogs import GenericStringEditDialog,\
    GenericStringSelectionDialog, GenericBooleanSelectionDialog
from manual_tester import AbstractComponentTest, TestRunner
from alexpresenters.components.references.eventcrossreferencespresenter \
    import EventCrossReferencesPresenter

class DateEntryWidgetTest(AbstractComponentTest):
    
    def __init__(self):
        super().__init__()
        self.name = "Date entry widget"
        
    def test_component(self, master, message_label):
        super().test_component(master, message_label)
        self.entry_widget = AlexDateEntry(self.master)
        self.entry_widget.pack(side=TOP, fill=BOTH, expand=TRUE)
        Button(self.master,
               text="Get entry",
               command=self._show_result).pack(side=TOP)

    def _show_result(self):
        try:
            date = self.entry_widget.get()
            self.message_label.set(date)
        except InvalidDateException as e:
            self.message_label.set(e)
            

class GenericStringEditDialogTest(AbstractComponentTest):
    '''
    classdocs
    '''

    def __init__(self):
        super().__init__()
        self.name = "Generic string edit dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        self.dialog = GenericStringEditDialog()
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        result = self.dialog.activate(self.master, label="Edit label", initvalue="Init value")
        self.message_label.set("Text is now: %s" % result)

class GenericStringSelectionDialogTest(AbstractComponentTest):
    '''
    classdocs
    '''

    def __init__(self):
        super().__init__()
        self.name = "Generic string selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        self.dialog = GenericStringSelectionDialog()
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        result = self.dialog.activate(self.master, label="Selection", choices=('one', 'two', 'three'))
        self.message_label.set("Selection was: %s" % result)

class GenericBooleanSelectionDialogTest(AbstractComponentTest):
    '''
    classdocs
    '''

    def __init__(self):
        super().__init__()
        self.name = "Generic boolean selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        self.dialog = GenericBooleanSelectionDialog()
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        result = self.dialog.activate(self.master, question="Are you lonesome tonight?")
        self.message_label.set("Selection was: %s" % result)

class EventSelectionDialogTest(AbstractComponentTest):
    '''
    classdocs
    '''

    def __init__(self):
        super().__init__()
        self.name = "Event selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        self.systematic_references_presenter = EventSelectionPresenter(EventServiceStub())
        self.dialog = EventSelectionDialog(self.systematic_references_presenter)
        Button(master, text='Start wizard', command=self._start_wizard).pack()

    def _start_wizard(self):
        result = self.dialog.activate(self.master)
        self.message_label.set("Selected event: %s" % result)

#class SystematicPointSelectionTest:
#        
#    def __init__(self):
#        super().__init__()
#        self.name = "Systematic node selection"
#        
#    def test_component(self, master, message_label):
#        self.master = master
#        self.message_label = message_label
#        presenter = SystematicPointSelectionPresenter(SystematicServiceStub())
#        self.dialog = SystematicPointSelectionDialog(presenter)
#        Button(self.master, text='Start dialog', command=self._start_dialog).pack()
#
#    def _start_dialog(self):
#        result = self.dialog.activate()
#        self.message_label.set("Selection: %s Type: %s" % (result, type(result)))
    
class DocumentEventReferencesTest(AbstractComponentTest):
    '''
    Test class to test the working of the widget. The systematic_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the presenter.
    '''

    def __init__(self):
        super().__init__()
        self.name = "Document event references"

    def create_mocks_and_stubs(self):
        self.reference_service = ReferenceServiceStub()
        self.event_service = EventServiceStub()

    def create_view(self, master):
        self.document_event_references_presenter = DocumentEventReferencesPresenter(
            self.message_broker,
            self.reference_service)
        dialog_presenter = EventSelectionPresenter(self.event_service)
        dialog_view = EventSelectionDialog(dialog_presenter)
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

class MessageBarTest(AbstractComponentTest):
    '''
    Test class to test the working of the widget. The systematic_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the presenter.
    '''

    def __init__(self):
        super().__init__()
        self.name = "Message bar"

    def create_view(self, master):
        self.message_bar = AlexMessageBar(master,)
        self.message_broker.subscribe(self.message_bar)
        self.message_bar.pack(side=TOP)
        
    def add_button(self, master):

        message = Message(ERROR_MESSAGE, messagetype='error', message='An error has occurred')
        button = Button(master, text='Send error message',
                                command=lambda m=message: self.message_broker.send_message(m))
        button.pack(side=TOP)

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_view(master)
        self.add_button(master)

#class DocumentSystematicReferencesTest(AbstractComponentTest):
#        
#    def __init__(self):
#        super().__init__()
#        self.name = "Document systematic references"
#
#    def create_mocks_and_stubs(self):
#        self.systematic_service = SystematicServiceStub()
#    
#    def create_widget(self, master):
#    
#        self.systematic_references_presenter = DocumentSystematicReferencesPresenter(
#            self.message_broker,
#            self.systematic_service)
#        self.systematic_point_selection_presenter = SystematicPointSelectionPresenter(
#            self.systematic_service)
#        self.systematic_point_selection_dialog = SystematicPointSelectionDialog(
#            self.systematic_point_selection_presenter)
#        view = DocumentSystematicReferenceView(
#            master,
#            self.systematic_references_presenter,
#            self.systematic_point_selection_dialog)
#        view.pack(side=TOP)
#
#    def add_button(self, master, number):
#        Button(master, 
#            text='Change to doc %d' % number,
#            command=lambda n=number: self.send_message(n)).pack(side=TOP)
#
#    def send_message(self, number):
#        message = Message(REQ_SET_DOCUMENT, document=Document(number))
#        self.message_broker.send_message(message)
#        
#    def test_component(self, master, message_label):
#        self.message_label = message_label
#        self.create_mocks_and_stubs()
#        self.create_widget(master)
#        self.add_button(master, 1)
#        self.add_button(master, 2)
        
class DocumentFileReferencesTest(AbstractComponentTest):
        
    def __init__(self):
        super().__init__()
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

class EventCrossReferencesTest(AbstractComponentTest):
    '''
    Test class to test the working of the widget. The event_cross_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the event_cross_references_presenter.
    '''
    def __init__(self):
        super().__init__()
        self.name = "Event cross references"

    def create_mocks_and_stubs(self):
        self.service = EventServiceStub()

    def create_view(self, master):
        self.event_cross_references_presenter = EventCrossReferencesPresenter(
            self.message_broker,
            self.service)
        self.event_selection_presenter = EventSelectionPresenter(
            self.service)
        self.event_selection_dialog = EventSelectionDialog(
            self.event_selection_presenter)
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
        
class FilterDialogsTest(AbstractComponentTest):
    '''
    Manual test for filter dialogs
    '''
    def __init__(self):
        super().__init__()
        self.name = "Filter dialogs"

    def create_views(self):
        
        self.generic_filter_dialog = GenericFilterDialog(GenericFilterDialogPresenter())

        self.document_filter_dialog = DocumentFilterDialog(DocumentFilterDialogPresenter())

        self.event_filter_dialog = EventFilterDialog(EventFilterDialogPresenter())

    def add_buttons(self, master):
        Button(
                master,
                text="Start generic filter dialog",
                command=lambda: self._show_generic(master)).pack(side=TOP)
            
        Button(
                master,
                text="Start document filter dialog",
                command=lambda: self._show_document_filter(master)).pack(side=TOP)

        Button(
                master,
                text="Start event filter dialog",
                command=lambda: self._show_event_filter(master)).pack(side=TOP)

            
    def _create_searchterm_string(self, filter_object):
        if not len(filter_object.searchterms):
            return ""
        return reduce(lambda s1, s2: "%s - %s" % (s1, s2), filter_object.searchterms)
                        
    def _show_generic(self, master):
        filter_object = self.generic_filter_dialog.activate(master)
        if not filter_object:
            self.message_label.set('')
            return
        self.message_label.set(self._create_searchterm_string(filter_object))

    def _show_document_filter(self, master):
        filter_object = self.document_filter_dialog.activate(master)
        if not filter_object:
            self.message_label.set('')
            return
        self.message_label.set("%s - %s" % (self._create_searchterm_string(filter_object),
                                        filter_object.location))
    def _show_event_filter(self, master):
        filter_object = self.event_filter_dialog.activate(master)
        if not filter_object:
            self.message_label.set('')
            return
        self.message_label.set("%s - %s - %s - %s - %s" % (
            self._create_searchterm_string(filter_object),
            filter_object.earliest_date,
            filter_object.latest_date,
            filter_object.local_only,
            filter_object.unverified_only))

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_views()
        self.add_buttons(master)

class LoginDialogTest(AbstractComponentTest):

    def __init__(self):
        super().__init__()
        self.name = "Login dialog"

    def create_mocks_and_stubs(self):
        creator1 = Creator(1)
        creator1.name = 'Max Mustermann'
        creator2 = Creator(2)
        creator2.name = 'Erna Musterfrau'
        self.creator_service = MagicMock(spec=CreatorService)
        self.creator_service.find_all_active_creators.return_value = [creator1, creator2]
        self.login_creator_provider = LoginCreatorProvider()
        self.presenter = LoginDialogPresenter(self.creator_service, self.login_creator_provider)
        self.dialog = LoginDialog(self.presenter)
        
    def add_button(self):
    
        load_references_button = Button(self.master, text='Start dialog',
                                command=self._start_dialog)
        load_references_button.pack(side=TOP)
        
    def _start_dialog(self):
        
        self.dialog.activate(self.master)
        try:
            self.message_label.set("Creator is now %s" % self.login_creator_provider.creator.name )
        except AttributeError:
            self.message_label.set("No creator selected")

    def test_component(self, master, message_label):
        self.master = master
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.add_button()

class GraphicsViewerTest(AbstractComponentTest):

    def __init__(self):
        super().__init__()
        self.name = "Graphics viewer"
 
    def create_mocks_and_stubs(self):
        
        self.test_file = os.path.join(get_testfiles_dir(), "testfile.tif")
        self.test_file_info = DocumentFileInfo()
        self.test_file_info.resolution = 300
        
    def add_button(self):
    
        viewer_button = Button(self.master, text='Start viewer',
                                command=self._start_viewer)
        viewer_button.pack(side=TOP)
        
    def _start_viewer(self):
        viewer = GraphicsViewer()
        viewer.showFile(self.test_file, self.test_file_info)
        
    def test_component(self, master, message_label):
        self.master = master
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.add_button()

class ExternalViewerTest(AbstractComponentTest):

    def __init__(self):
        super().__init__()
        self.name = "External viewer"
 
    def create_mocks_and_stubs(self):
        
        self.test_file = os.path.join(get_testfiles_dir(), "testfile.pdf")
        self.test_file_info = DocumentFileInfo()
        self.test_file_info.resolution = 300
        
    def add_button(self):
    
        viewer_button = Button(self.master, text='Start viewer',
                                command=self._start_viewer)
        viewer_button.pack(side=TOP)
        
    def _start_viewer(self):
        viewer = ExternalViewer('/usr/bin/atril')
        viewer.showFile(self.test_file, self.test_file_info)
        
    def test_component(self, master, message_label):
        self.master = master
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.add_button()

if __name__ == '__main__':
    test_classes = []
    test_classes.append(DateEntryWidgetTest())
    test_classes.append(GenericStringEditDialogTest())
    test_classes.append(GenericStringSelectionDialogTest())
    test_classes.append(GenericBooleanSelectionDialogTest())
    test_classes.append(EventSelectionDialogTest())
#    test_classes.append(SystematicPointSelectionTest())
    test_classes.append(DocumentEventReferencesTest())
#    test_classes.append(DocumentSystematicReferencesTest())
    test_classes.append(DocumentFileReferencesTest())
    test_classes.append(EventCrossReferencesTest())
    test_classes.append(FilterDialogsTest())
    test_classes.append(MessageBarTest())
    test_classes.append(LoginDialogTest())
    test_classes.append(GraphicsViewerTest())
    test_classes.append(ExternalViewerTest())
    test_runner = TestRunner(test_classes)
    test_runner.run()

