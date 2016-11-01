'''
Created on 13.12.2015

@author: michael
'''
import unittest
from threading import Thread, Condition

from injector import Module, ClassProvider, singleton, Injector
from alexandriabase import baseinjectorkeys, AlexBaseModule
from tkgui import guiinjectorkeys
from tkgui.main import MainRunner
from alexandriabase.daos.basiccreatorprovider import BasicCreatorProvider
from alex_test_utils import TestEnvironment, setup_database_schema,\
    load_table_data, MODE_FULL
from alexandriabase.daos import DaoModule
from alexandriabase.services import ServiceModule
from alexpresenters import PresentersModule
from tkgui.mainwindows import MainWindowsModule
from tkgui.dialogs import DialogsTkGuiModule
from daotests.test_base import tables
from alexandriabase.base_exceptions import NoSuchEntityException
import os
from tkgui.mainwindows.EventWindow import EventWindow
import traceback
import sys
from alexandriabase.domain import AlexDate
from tkgui.mainwindows.BaseWindow import BaseWindow
from tkgui.components.references import WindowReferencesModule
import time
from tkinter import TclError

def set_date_range(dialog, start_date, end_date):
    dialog.days = [start_date.day, end_date.day]
    dialog.months = [start_date.month, end_date.month]
    dialog.years = [start_date.year, end_date.year]

def set_date(dialog, alex_date):
    dialog.days = [alex_date.day]
    dialog.months = [alex_date.month]
    dialog.years = [alex_date.year]

class CommandRunner(Thread):
    '''
    This class is used in the DialogExecutor to run commands
    from a separate thread. If a command fails with an
    exception it is repeated until it succeeds. Before the
    last command (which should close the dialog), there
    is some short pause to assure that the dialog is fully
    configured. This is quite bad, but can't be helped - at
    least I am at a loss to find a better solution.
    '''
    
    def __init__(self):
        super().__init__()
        self.command_queue = []
        self.verbose = False
        
    def add_command(self, command):
        self.command_queue.append(command)
        
    def run(self):
        while len(self.command_queue) > 1:
            try:
                execution_failed = False
                self.command_queue[0]()
            except Exception as ex:
                if self.verbose:
                    print(ex)
                    traceback.print_exc(file=sys.stderr)
                execution_failed = True
            if not execution_failed:
                del self.command_queue[0]
        # Wait a bit before issuing the closing command of the dialog
        time.sleep(0.1) # This is super ugly, but I found no other solution
        self.command_queue[0]()
                
class DialogExecutor:
    '''
    Opening a dialog blocks the current thread, so the commands
    for doing something in the dialog must be called from a separate
    thread. So we configure the commands to execute on the dialog
    in this class, start a new thread for them to be executed and
    then activate the dialog.
    '''
    
    def __init__(self):
        self.command_runner = CommandRunner()
        
    def add_command(self, command):
        self.command_runner.add_command(command)
        
    def run(self, dialog_command):
        self.command_runner.start()
        dialog_command()
        self.command_runner.join()
        
class GuiThread(Thread):
    '''
    Runs the tkinter application in a separate thread (to prevent blocking).
    '''

    def __init__(self, config_file_name):
        super().__init__()
        self.config_file_name = config_file_name
        self.condition = Condition()
        self.initialized = False

    def run(self):
        with self.condition:
            self.injector = Injector([
                                      AcceptanceTestModule(self.config_file_name),
                                      AlexBaseModule(),
                                      DaoModule(),
                                      ServiceModule(),
                                      PresentersModule(),
                                      MainWindowsModule(),
                                      DialogsTkGuiModule(),
                                      WindowReferencesModule()
                                      ])
            engine = self.injector.get(baseinjectorkeys.DBEngineKey)
            setup_database_schema(engine)
            load_table_data(tables, engine)
            main_runner = self.injector.get(guiinjectorkeys.MAIN_RUNNER_KEY)
            self.initialized = True
            self.condition.notify() 
        main_runner.run()

class AcceptanceTestModule(Module):
    
    def __init__(self, config_file):
        self.config_file = config_file
        
    def configure(self, binder):
        binder.bind(baseinjectorkeys.CONFIG_FILE_KEY, to=self.config_file)
        binder.bind(guiinjectorkeys.MAIN_RUNNER_KEY,
                    ClassProvider(MainRunner), scope=singleton)
        binder.bind(baseinjectorkeys.CreatorProvider,
                    ClassProvider(BasicCreatorProvider), scope=singleton)

class Test(unittest.TestCase):


    def run_safe(self, command):
        command_succeeded = False
        while not command_succeeded:
            try:
                command()
                command_succeeded = True
            except:
                pass

    def setUp(self):
        self.env = TestEnvironment(mode=MODE_FULL)

        self.gui_thread = GuiThread(self.env.config_file_name)
        self.gui_thread.start()
        with self.gui_thread.condition:
            while not self.gui_thread.initialized:
                self.gui_thread.condition.wait()
        self.injector = self.gui_thread.injector
        self.success = False
        self.event_window = self.injector.get(guiinjectorkeys.EVENT_WINDOW_KEY)
        self.event_window_presenter = self.injector.get(guiinjectorkeys.EVENT_WINDOW_PRESENTER_KEY)
        self.document_window = self.injector.get(guiinjectorkeys.DOCUMENT_WINDOW_KEY)
        self.document_window_presenter = self.injector.get(guiinjectorkeys.DOCUMENT_WINDOW_PRESENTER_KEY)
        print("OK.\nTests start running...")

    def tearDown(self):
        if not self.success:
            print("FAILED")
            self.event_window_presenter.quit()
            print("\nAcceptance test failed!")
        self.gui_thread.join()

    def test_acceptance(self):

        # Navigation
        print("\nChecking navigation")
        print("===================")
        self.check_initial_records_shown()
        self.check_goto_last_event()      
        self.check_goto_last_document()
        self.check_goto_first_event()
        self.check_goto_first_document()
        self.check_goto_next_event()
        self.check_goto_next_document()
        self.check_goto_previous_event()
        self.check_goto_previous_document()
        self.check_goto_event()
        self.check_goto_document()
        
        # Filtering
        print("\nChecking filtering")
        print("==================")
        self.check_filtering_events()
        self.check_filtering_events_with_empty_selection()
        self.check_filtering_documents()
        self.check_filtering_documents_with_empty_selection()
        
        # References
        print("\nChecking references")
        print("===================")

        # Event cross references
        self.check_event_cross_reference_goto()
        self.check_event_cross_reference_new()
        self.check_event_cross_reference_delete()
        print("")
        self.check_document_systematic_reference_new()
        self.check_document_systematic_reference_delete()
        
        # Save
        print("\nChecking saving")
        print("===============")

        self.check_save_event()
        self.check_save_document()
        
        # Create new
        print("\nChecking creation")
        print("=================")
        self.check_create_event()
        self.check_create_document()
        
        # Deleting
        print("\nChecking deleting")
        print("=================")

        self.check_deleting_event()
        self.check_deleting_of_document()
        
        # Quit
        print("\nChecking quit")
        print("=============")
        self.check_quit_works()
        self.success = True
        
        print("\nAcception test succeeded.\n")
    
    def check_goto_last_event(self):
        print("Checking going to last event works...", end='')
        self.event_window_presenter.goto_last()
        self.assert_that_event_is(1961050101)
        self.assert_that_event_description_is("Viertes Ereignis")
        print("OK")
    
    def check_goto_first_event(self):
        print("Checking going to first event works...", end='')
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1940000001)
        self.assert_that_event_description_is("Erstes Ereignis")
        print("OK")

    def check_goto_next_event(self):
        print("Checking going to next event works...", end='')
        self.event_window_presenter.goto_last()
        # Wrap arount
        self.event_window_presenter.goto_next()
        self.assert_that_event_is(1940000001)
        self.assert_that_event_description_is("Erstes Ereignis")
        self.event_window_presenter.goto_next()
        self.assert_that_event_is(1950000001)
        self.assert_that_event_description_is("Zweites Ereignis")
        print("OK")

    def check_goto_previous_event(self):
        print("Checking going to previous event works...", end='')
        self.event_window_presenter.goto_first()
        # Wrap arount
        self.event_window_presenter.goto_previous()
        self.assert_that_event_is(1961050101)
        self.assert_that_event_description_is("Viertes Ereignis")
        self.event_window_presenter.goto_previous()
        self.assert_that_event_is(1960013001)
        self.assert_that_event_description_is("Drittes Ereignis")
        print("OK")
        
    def check_goto_event(self):
        print("Checking going to nearest selected event works...", end='')
        dialog = self.event_window.dialogs[BaseWindow.GOTO_DIALOG]

        dialog_executor = DialogExecutor()
        dialog_executor.add_command(lambda: set_date(dialog, AlexDate(1960, 1, 1)))
        dialog_executor.add_command(lambda: dialog.dialog.invoke(0))
        dialog_executor.run(self.event_window_presenter.goto_record)

        self.assert_that_event_is(1960013001)
        print("OK")

    def check_goto_document(self):
        print("Checking going to nearest selected document works...", end='')
        dialog = self.document_window.dialogs[BaseWindow.GOTO_DIALOG]

        dialog_executor = DialogExecutor()
        dialog_executor.add_command(lambda: dialog._entry_widget.set("7"))
        dialog_executor.add_command(lambda: dialog.dialog.invoke(0))
        dialog_executor.run(self.document_window_presenter.goto_record)

        self.assert_that_document_is(8)
        print("OK")

    def check_filtering_events(self):
        print("Checking filtering events works...", end='')
        dialog = self.event_window.dialogs[BaseWindow.FILTER_DIALOG]

        def set_earliest_date():
            dialog.earliest_date = AlexDate(1961, 1, 1)

        dialog_executor = DialogExecutor()            
        dialog_executor.add_command(set_earliest_date)
        dialog_executor.add_command(lambda: dialog.dialog.invoke(0))
        
        # Turn filtering on
        dialog_executor.run(self.event_window_presenter.toggle_filter)
        
        self.assert_that_event_is(1961050101)
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1961050101)

        # Turn filtering off
        self.event_window_presenter.toggle_filter()

        self.assert_that_event_is(1961050101)
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1940000001)

        print("OK")
        
    def check_filtering_events_with_empty_selection(self):
        print("Checking filtering events works even if nothing is selected...", end='')
        dialog = self.event_window.dialogs[BaseWindow.FILTER_DIALOG]

        def set_earliest_date():
            dialog.earliest_date = AlexDate(1980, 1, 1)
            
        dialog_executor = DialogExecutor()
        dialog_executor.add_command(set_earliest_date)
        dialog_executor.add_command(lambda: dialog.dialog.invoke(0))
        
        # Turn filtering on
        dialog_executor.run(self.event_window_presenter.toggle_filter)

        self.assert_no_event()
        self.event_window_presenter.goto_first()
        self.assert_no_event()
        
        # Turn filtering off
        self.event_window_presenter.toggle_filter()

        self.assert_no_event()
        self.event_window_presenter.goto_first()
        self.assert_that_event_is(1940000001)

        print("OK")

    def check_filtering_documents(self):
        print("Checking filtering documents works...", end='')
        dialog = self.document_window.dialogs[BaseWindow.FILTER_DIALOG]

        dialog_executor = DialogExecutor()
        dialog_executor.add_command(lambda: dialog.search_term_entries[0].set("Zweites"))
        dialog_executor.add_command(lambda: dialog.dialog.invoke(0))
        
        # Turn filtering on
        dialog_executor.run(self.document_window_presenter.toggle_filter)

        self.assert_that_document_is(4)
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(4)
        self.document_window_presenter.goto_last()
        self.assert_that_document_is(4)

        # Turn filtering off
        self.document_window_presenter.toggle_filter()

        self.assert_that_document_is(4)
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(1)
        self.document_window_presenter.goto_last()
        self.assert_that_document_is(8)

        print("OK")

    def check_filtering_documents_with_empty_selection(self):
        print("Checking filtering documents works even if nothing is selected...", end='')
        dialog = self.document_window.dialogs[BaseWindow.FILTER_DIALOG]

        dialog_executor = DialogExecutor()
        dialog_executor.add_command(lambda: dialog.search_term_entries[0].set("no match"))
        dialog_executor.add_command(lambda: dialog.dialog.invoke(0))
        
        # Turn filtering on
        dialog_executor.run(self.document_window_presenter.toggle_filter)

        self.assert_no_document()
        self.document_window_presenter.goto_first()
        self.assert_no_document()
        
        # Turn filtering off
        self.document_window_presenter.toggle_filter()

        self.assert_no_document()
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(1)

        print("OK")

    def check_event_cross_reference_goto(self):
        print("Checking goto event cross reference...", end='')
        reference= self.event_window.references[0]
        
        self.event_window_presenter.goto_first()
        
        self.assert_that_event_is(1940000001)

        reference.presenter.goto_event()
        
        self.assert_that_event_is(1950000001)
        
        print("OK")
        
    def check_event_cross_reference_new(self):
        print("Checking create new event cross reference...", end='')
        reference= self.event_window.references[0]
        dialog = reference.event_selection_dialog
        
        self.event_window_presenter.goto_first()

        self.assertEqual(len(reference._items), 2)        

        dialog_executor = DialogExecutor()
        dialog_executor.add_command(lambda: dialog.presenter.view.date_entry.set(AlexDate(1960,1,30)))
        dialog_executor.add_command(lambda: dialog.presenter.update_event_list())
        dialog_executor.add_command(lambda: dialog.presenter.view.event_list_box.setvalue("%s" % dialog.presenter.view.event_list[0]))
        dialog_executor.add_command(lambda: dialog.presenter.close())
        dialog_executor.run(reference.presenter.add_new_cross_reference)

        self.assertEqual(len(reference._items), 3)
                
        print("OK")

    def check_event_cross_reference_delete(self):
        print("Checking delete event cross reference...", end='')
        reference= self.event_window.references[0]
        
        self.event_window_presenter.goto_first()

        self.assertEqual(len(reference._items), 3)
        
        reference.listbox.setvalue("%s" % self.get_event(1960013001))       

        reference.presenter.delete_cross_reference()

        self.assertEqual(len(reference._items), 2)
                
        print("OK")
        
    def check_document_systematic_reference_new(self):
        print("Checking create new document systematic reference...", end='')
        reference = self.document_window.references[0]
        self.document_window_presenter.goto_first()
        self.assertEqual(len(reference._items), 3)
        
        dialog_executor = DialogExecutor()
        dialog_executor.add_command(lambda: reference.systematic_point_dialog.tree_widget.tree_root.children[1].select())
        dialog_executor.add_command(lambda: reference.systematic_point_dialog.dialog.invoke(0))
        dialog_executor.run(reference.presenter.add_new_systematic_point)

        self.assertEqual(len(reference._items), 4)
        
        print("OK")
    
    def check_document_systematic_reference_delete(self):
        print("Checking delete document systematic reference...", end='')
        reference = self.document_window.references[0]
        self.document_window_presenter.goto_first()
        self.assertEqual(len(reference._items), 4)
        
        reference.listbox.setvalue("2: 2")
        reference.presenter.delete_selected_systematic_point()

        self.assertEqual(len(reference._items), 3)
        
        print("OK")

    def check_deleting_event(self):
        print("Checking deleting of event works...", end='')
        self.event_window_presenter.goto_last()
        self.event_window_presenter.delete()
        self.assert_that_event_is(1960013001)
        self.assert_that_event_description_is("Drittes Ereignis")
        self.assert_no_such_event(1961050101)

        print("OK")
        
    def check_save_event(self):
        print("Checking saving of event works...", end='')
        self.event_window_presenter.goto_first()
        self.event_window._description_widget.set("First event with new description")
        event = self.get_event(1940000001)
        self.assertEqual("Erstes Ereignis", event.description)
        self.event_window_presenter.goto_next()
        event = self.get_event(1940000001)
        self.assertEqual("First event with new description", event.description)
        print("OK")
        
    def check_create_event(self):
        print("Checking creation of event works...", end='')

        dialog = self.event_window.dialogs[EventWindow.DATE_RANGE_DIALOG]

        dialog_executor = DialogExecutor()
        dialog_executor.add_command(lambda: set_date_range(dialog, AlexDate(1940), AlexDate(1950)))
        dialog_executor.add_command(lambda: dialog.dialog.invoke(0))
        dialog_executor.run(self.event_window_presenter.create_new)

        self.event_window._description_widget.set("Completely new event.")
        self.event_window_presenter.goto_first()
        self.event_window_presenter.goto_next()
        
        event = self.event_window.entity
        self.assertEqual(1940000002, event.id)
        self.assertEqual("Completely new event.", event.description)
                
        print("OK")
        
    def check_goto_last_document(self):
        print("Checking going to last document works...", end='')
        self.document_window_presenter.goto_last()
        self.assert_that_document_is(8)
        self.assert_that_document_description_is("Drittes Dokument")  
        print("OK")

    def check_goto_first_document(self):
        print("Checking going to first document works...", end='')
        self.document_window_presenter.goto_first()
        self.assert_that_document_is(1)
        self.assert_that_document_description_is("Erstes Dokument")  
        print("OK")

    def check_goto_next_document(self):
        print("Checking going to next document works...", end='')
        self.document_window_presenter.goto_last()
        # Wrap around
        self.document_window_presenter.goto_next()
        self.assert_that_document_is(1)
        self.assert_that_document_description_is("Erstes Dokument")  
        self.document_window_presenter.goto_next()
        self.assert_that_document_is(4)
        self.assert_that_document_description_is("Zweites Dokument")  
        print("OK")

    def check_goto_previous_document(self):
        print("Checking going to previous document works...", end='')
        self.document_window_presenter.goto_first()
        # Wrap around
        self.document_window_presenter.goto_previous()
        self.assert_that_document_is(8)
        self.assert_that_document_description_is("Drittes Dokument")  
        self.document_window_presenter.goto_previous()
        self.assert_that_document_is(4)
        self.assert_that_document_description_is("Zweites Dokument")  
        print("OK")

    def check_initial_records_shown(self):
        print("Checking the windows show the inital records...", end='')
        self.assert_that_event_is(1940000001)
        self.assert_that_document_is(1)
        self.assert_that_document_description_is("Erstes Dokument")  
        print("OK")
        
    def check_deleting_of_document(self):
        print("Checking deleting of document works...", end='')
        self.assertTrue(os.path.isfile(self.env.file_paths[1]))
        self.assertTrue(os.path.isfile(self.env.file_paths[2]))
        self.assertTrue(os.path.isfile(self.env.file_paths[3]))

        self.document_window_presenter.goto_first()
        self.document_window_presenter.delete()

        self.assertFalse(os.path.isfile(self.env.file_paths[1]))
        self.assertFalse(os.path.isfile(self.env.file_paths[2]))
        self.assertFalse(os.path.isfile(self.env.file_paths[3]))
        
        self.assert_no_such_document(1)
        self.assert_no_such_document_file_info(1)
        self.assert_no_such_document_file_info(2)
        self.assert_no_such_document_file_info(3)
        print("OK")
        
    def check_save_document(self):
        print("Checking saving of document works...", end='')
        self.document_window_presenter.goto_first()
        self.document_window._description_widget.set("First document with new description")
        document = self.get_document(1)
        self.assertEqual("Erstes Dokument", document.description)
        self.document_window_presenter.goto_next()
        document = self.get_document(1)
        self.assertEqual("First document with new description", document.description)
        print("OK")
        
    def check_create_document(self):
        print("Checking creating of new document works...", end='')
        self.document_window_presenter.create_new()
        self.document_window._description_widget.set("Completely new document.")
        self.assert_no_such_document(11)
        self.document_window_presenter.goto_next()
        self.assert_no_such_document(11)
        self.document_window_presenter.goto_first()
        document = self.get_document(11)
        self.assertEqual(11, document.id)
        self.assertEqual("Completely new document.", document.description)
        self.document_window_presenter.goto_last()
        self.assertEqual(11, self.document_window.entity.id)
        self.assertEqual("Completely new document.", self.document_window.entity.description)
        print("OK")

    def assert_that_event_description_is(self, description):
        self.assertEquals(description, self.event_window._description_widget.get())

    def assert_that_event_is(self, event_id):
        self.assertEquals(event_id, self.event_window.entity.id)
    
    def assert_no_event(self):
        self.assertEquals(None, self.event_window.entity)
        self.assert_that_event_description_is('')
    
    def assert_no_document(self):
        self.assertEquals(None, self.document_window.entity)
        self.assert_that_document_description_is('')
    
    def assert_that_document_description_is(self, description):
        self.assertEquals(description, self.document_window._description_widget.get())

    def assert_that_document_is(self, document_id):
        self.assertEquals(document_id, self.document_window.entity.id)

    def assert_no_such_event(self, event_id):
        self.assert_no_such_entity(event_id, baseinjectorkeys.EreignisDaoKey)

    def assert_no_such_document(self, document_id):
        self.assert_no_such_entity(document_id, baseinjectorkeys.DokumentDaoKey)

    def assert_no_such_document_file_info(self, document_file_info_id):
        self.assert_no_such_entity(document_file_info_id, baseinjectorkeys.DOCUMENT_FILE_INFO_DAO_KEY)
        
    def assert_no_such_entity(self, entity_id, dao_key):
        expected_exception_thrown = False
        try:
            self.get_entity(entity_id, dao_key)
        except NoSuchEntityException:
            expected_exception_thrown = True
        self.assertTrue(expected_exception_thrown)

    def check_quit_works(self):
        print("Checking quit works...", end='')
        self.event_window_presenter.quit()
        print("OK")

    def get_event(self, entity_id):
        return self.get_entity(entity_id, baseinjectorkeys.EreignisDaoKey)

    def get_document(self, document_id):
        return self.get_entity(document_id, baseinjectorkeys.DokumentDaoKey)

    def get_entity(self, entity_id, dao_key):
        dao = self.injector.get(dao_key)
        return dao.get_by_id(entity_id)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()