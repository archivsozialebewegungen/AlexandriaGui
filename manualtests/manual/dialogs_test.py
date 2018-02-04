'''
Created on 22.01.2016

@author: michael
'''
from tkgui.Dialogs import GenericBooleanSelectionDialog,\
    GenericStringSelectionDialog, GenericStringEditDialog, YearSelectionDialog,\
    SimpleDateSelectionDialog, EventIdSelectionDialog, DateRangeSelectionDialog,\
    DocumentIdSelectionDialog, EventSelectionWizard, EventConfirmationDialog,\
    EventTypeSelectionDialog, GenericFilterDialog, DocumentFilterDialog,\
    EventFilterDialog, LoginDialog, FileSelectionDialog
from alexpresenters.DialogPresenters import GenericInputDialogPresenter,\
    YearSelectionDialogPresenter, DateSelectionDialogPresenter,\
    EventIdSelectionDialogPresenter, DateRangeSelectionDialogPresenter,\
    DocumentIdSelectionDialogPresenter, EventSelectionPresenter,\
    AbstractInputDialogPresenter, EventTypeSelectionPresenter,\
    GenericFilterDialogPresenter, DocumentFilterDialogPresenter,\
    EventFilterDialogPresenter, LoginDialogPresenter
from tkinter.ttk import Button
from tkinter.constants import TOP
from _functools import reduce
from alexandriabase.domain import Creator, DocumentFileInfo, Event, AlexDate
from unittest.mock import MagicMock
from alexandriabase.services.creatorservice import CreatorService
import os
from alex_test_utils import get_testfiles_dir
from manual.manual_tester import AbstractComponentTest, TestRunner
from WindowTestHelpers import EventServiceStub
from alexandriabase.config import Config
from tkgui.FileViewers import GraphicsViewer, ExternalViewer

class DialogTest(AbstractComponentTest):
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        super().__init__()

class DialogTestRunner(TestRunner):
    
    def create_test_instances(self, test_classes):
        self.test_instances = []
        for test_class in test_classes:
            self.test_instances.append(test_class(self.window_manager))


class GenericStringEditDialogTest(DialogTest):
    '''
    classdocs
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Generic string edit dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.dialog = GenericStringEditDialog(self.window_manager,
                                              GenericInputDialogPresenter())
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        self.dialog.activate(self.callback, 
                             label="Edit label",
                             initvalue="Init value")
        
    def callback(self, value):
        if value is None:
            self.message_label.set("You canceled.")
        else:
            self.message_label.set("Your input text was '%s'." % value)

class GenericStringSelectionDialogTest(DialogTest):
    '''
    classdocs
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Generic string selection dialog"
        self.choices = ('one', 'two', 'three')

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        self.dialog = GenericStringSelectionDialog(self.window_manager,
                                                   GenericInputDialogPresenter())
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        self.dialog.activate(self.callback, label="Selection", choices=self.choices)

    def callback(self, value):
        if value is None:
            self.message_label.set("Your canceled.")
        else:
            self.message_label.set("You selected '%s'." % self.choices[value])

class GenericBooleanSelectionDialogTest(DialogTest):
    '''
    classdocs
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Generic boolean selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        self.dialog = GenericBooleanSelectionDialog(self.window_manager,
                                                    GenericInputDialogPresenter())
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        self.dialog.activate(self.callback, question="Are you lonesome tonight?")

    def callback(self, value):
        if value:
            self.message_label.set("Sorry to hear you're lonesome.")
        else:
            self.message_label.set("Glad you're not lonesome.")

class SimpleDateSelectionDialogTest(DialogTest):
    '''
    classdocs
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Date selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        
        year_selection_dialog = YearSelectionDialog(self.window_manager,
                                                    YearSelectionDialogPresenter())
        self.dialog = SimpleDateSelectionDialog(self.window_manager,
                                                DateSelectionDialogPresenter(),
                                                year_selection_dialog)
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        self.dialog.activate(self.callback)

    def callback(self, value):
        if value is None:
            self.message_label.set("You canceled.")
        else:
            self.message_label.set("Selected date: %s" % value)

class EventIdSelectionDialogTest(DialogTest):
    '''
    classdocs
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Event id selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        
        year_selection_dialog = YearSelectionDialog(self.window_manager,
                                                    YearSelectionDialogPresenter())
        self.dialog = EventIdSelectionDialog(self.window_manager,
                                                EventIdSelectionDialogPresenter(),
                                                year_selection_dialog)
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        self.dialog.activate(self.callback)

    def callback(self, value):
        if value is None:
            self.message_label.set("You canceled.")
        else:
            self.message_label.set("Selected id: %s" % value)

class DateRangeSelectionDialogTest(DialogTest):
    '''
    classdocs
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Date range selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        
        year_selection_dialog = YearSelectionDialog(self.window_manager,
                                                    YearSelectionDialogPresenter())
        self.dialog = DateRangeSelectionDialog(self.window_manager,
                                                DateRangeSelectionDialogPresenter(),
                                                year_selection_dialog)
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        self.dialog.activate(self.callback)

    def callback(self, value):
        if value is None:
            self.message_label.set("You canceled.")
        else:
            self.message_label.set("Selected date range: %s" % value)

class DocumentIdSelectionDialogTest(DialogTest):
    '''
    classdocs
    '''

    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Document id selection dialog"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        
        self.dialog = DocumentIdSelectionDialog(self.window_manager,
                                                DocumentIdSelectionDialogPresenter)
        Button(master, text='Start dialog', command=self._start_dialog).pack()

    def _start_dialog(self):
        self.dialog.activate(self.callback)

    def callback(self, value):
        if value is None:
            self.message_label.set("You canceled.")
        else:
            self.message_label.set("Selected id: %s" % value)

class FilterDialogsTest(DialogTest):
    '''
    Manual test for filter dialogs
    '''
    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Filter dialogs"

    def create_views(self):
        
        self.generic_filter_dialog = GenericFilterDialog(
            self.window_manager,
            GenericFilterDialogPresenter())

        self.document_filter_dialog = DocumentFilterDialog(
            self.window_manager,
            DocumentFilterDialogPresenter())

        self.event_filter_dialog = EventFilterDialog(
            self.window_manager,
            EventFilterDialogPresenter())

    def add_buttons(self, master):
        Button(
                master,
                text="Start generic filter dialog",
                command=self._show_generic).pack(side=TOP)
            
        Button(
                master,
                text="Start document filter dialog",
                command=self._show_document_filter).pack(side=TOP)

        Button(
                master,
                text="Start event filter dialog",
                command=self._show_event_filter).pack(side=TOP)

            
    def _create_searchterm_string(self, filter_object):
        if not len(filter_object.searchterms):
            return ""
        return reduce(lambda s1, s2: "%s - %s" % (s1, s2), filter_object.searchterms)
                        
    def _show_generic(self):
        self.generic_filter_dialog.activate(self._generic_callback)
        
    def _generic_callback(self, filter_object):
        if not filter_object:
            self.message_label.set('You canceled!')
            return
        self.message_label.set(self._create_searchterm_string(filter_object))

    def _show_document_filter(self):
        self.document_filter_dialog.activate(self._document_filter_callback)
        
    def _document_filter_callback(self, filter_object):
        if not filter_object:
            self.message_label.set('You canceled!')
            return
        self.message_label.set("%s - %s" % (self._create_searchterm_string(filter_object),
                                        filter_object.signature))
        
    def _show_event_filter(self):
        self.event_filter_dialog.activate(self._event_filter_callback)
        
    def _event_filter_callback(self, filter_object):
        if not filter_object:
            self.message_label.set('You canceled!')
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

    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager
        self.name = "Login dialog"

    def create_mocks_and_stubs(self):
        creator1 = Creator(1)
        creator1.name = 'Max Mustermann'
        creator2 = Creator(2)
        creator2.name = 'Erna Musterfrau'
        self.creator_service = MagicMock(spec=CreatorService)
        self.creator_service.find_all_active_creators.return_value = [creator1, creator2]
        self.presenter = LoginDialogPresenter(self.creator_service)
        self.dialog = LoginDialog(self.window_manager, self.presenter)
        
    def add_button(self):
    
        load_references_button = Button(self.master, text='Start dialog',
                                command=self._start_dialog)
        load_references_button.pack(side=TOP)
        
    def _start_dialog(self):
        
        creator = self.dialog.activate()
        try:
            self.message_label.set("Creator is now %s" % creator.name )
        except AttributeError:
            self.message_label.set("No creator selected")

    def test_component(self, master, message_label):
        self.master = master
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.add_button()

class GraphicsViewerTest(AbstractComponentTest):

    def __init__(self, window_manager):
        self.window_manager = window_manager
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
        viewer = GraphicsViewer(self.window_manager)
        viewer.showFile(self.test_file, self.test_file_info)
        
    def test_component(self, master, message_label):
        self.master = master
        self.message_label = message_label
        self.create_mocks_and_stubs()
        self.add_button()
        
class ExternalViewerTest(AbstractComponentTest):

    def __init__(self, window_manager):
        self.window_manager = window_manager
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


class EventSelectionWizardTest(DialogTest):
    
    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Event selection wizard"
        
    def start_dialog(self):
        
        service = EventServiceStub()
        presenter = EventSelectionPresenter(service)
        dialog = EventSelectionWizard(self.window_manager, presenter)
        dialog.activate(self.callback)    
        
        
    def callback(self, value):
        
        self.message_label.set(value)
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        Button(master, text="Start wizard", command=self.start_dialog).pack()

class EventConfirmationDialogTest(DialogTest):
    
    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Event confirmation"
        
    def start_dialog(self):
        
        event_list = (Event(1974010501), Event(1974010502))
        event_list[0].description = "Event 1"
        event_list[1].description = "Event 2"
        presenter = AbstractInputDialogPresenter()
        dialog = EventConfirmationDialog(self.window_manager, presenter)
        dialog.activate(self.callback,
                        event_list=event_list,
                        date=AlexDate(1974, 5, 1))    
        
    def callback(self, value):
        
        self.message_label.set("%s (%s)" % (value, type(value)))
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        Button(master, text="Start dialog", command=self.start_dialog).pack()

class EventTypeSelectionDialogTest(DialogTest):
    
    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "Event type selection"
        
    def start_dialog(self):

        event_service = EventServiceStub()
        presenter = EventTypeSelectionPresenter(event_service)
        dialog = EventTypeSelectionDialog(self.window_manager, presenter)
        dialog.activate(self.callback, "Test selection")    
        
    def callback(self, value):
        
        self.message_label.set(value)
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        Button(master, text="Start dialog", command=self.start_dialog).pack()


class FileSelectionDialogTest(DialogTest):
    
    def __init__(self, window_manager):
        super().__init__(window_manager)
        self.name = "File selection"
        config_mock = MagicMock(spec=Config)
        config_mock.filetypes = ['pdf']
        config_mock.filetypealiases = {}
        self.dialog = FileSelectionDialog(config_mock)
        
    def start_dialog_existing(self):

        self.dialog.activate(self.callback, new=False)    
        
    def start_dialog_new(self):

        self.dialog.activate(self.callback, new=True)    
        
    def callback(self, value):
        
        self.message_label.set(value)
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        Button(master, text="Existing file name", command=self.start_dialog_existing).pack()
        Button(master, text="New file name", command=self.start_dialog_new).pack()


if __name__ == '__main__':
    test_classes = []
    test_classes.append(GenericStringEditDialogTest)
    test_classes.append(GenericStringSelectionDialogTest)
    test_classes.append(GenericBooleanSelectionDialogTest)
    test_classes.append(SimpleDateSelectionDialogTest)
    test_classes.append(EventIdSelectionDialogTest)
    test_classes.append(DateRangeSelectionDialogTest)
    test_classes.append(DocumentIdSelectionDialogTest)
    test_classes.append(FilterDialogsTest)
    test_classes.append(LoginDialogTest)
    test_classes.append(GraphicsViewerTest)
    test_classes.append(ExternalViewerTest)
    test_classes.append(EventSelectionWizardTest)
    test_classes.append(EventConfirmationDialogTest)
    test_classes.append(EventTypeSelectionDialogTest)
    test_classes.append(FileSelectionDialogTest)
    test_runner = DialogTestRunner(test_classes)
    test_runner.run()

