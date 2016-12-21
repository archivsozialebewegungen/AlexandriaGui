'''
Created on 21.12.2016

@author: michael
'''
from threading import Thread
from time import sleep
from injector import Injector, Module, ClassProvider, singleton, provides,\
    inject
from alexandriabase import AlexBaseModule, baseinjectorkeys
from alexandriabase.base_exceptions import NoSuchEntityException
from alexandriabase.daos import DaoModule
from alexandriabase.daos.basiccreatorprovider import BasicCreatorProvider
from alexandriabase.services import ServiceModule
from alexpresenters import PresentersModule
from alexpresenters.messagebroker import CONF_DOCUMENT_WINDOW_READY,\
    CONF_EVENT_WINDOW_READY
from tkgui.mainwindows import MainWindowsModule
from tkgui.dialogs import DialogsTkGuiModule
from tkgui.components.references import WindowReferencesModule
from tkgui import guiinjectorkeys
from tkgui.main import SetupRunner, StartupTaskCheckDatabaseVersion, MainRunner,\
    StartupTaskPopulateWindows
from alex_test_utils import setup_database_schema, load_table_data,\
    TestEnvironment, MODE_FULL
from daotests.test_base import tables

def set_date_range(dialog, start_date, end_date):
    '''
    Helper function to set a data range in the dialog.
    '''
    dialog.days = [start_date.day, end_date.day]
    dialog.months = [start_date.month, end_date.month]
    dialog.years = [start_date.year, end_date.year]

def set_date(dialog, alex_date):
    '''
    Helper function to set a date in the dialog.
    '''
    dialog.days = [alex_date.day]
    dialog.months = [alex_date.month]
    dialog.years = [alex_date.year]

class DialogStarter(Thread):
    '''
    Dialogs block the current thread, so they need to
    be started in their own thread
    '''    
    def __init__(self, start_command):
        super().__init__()
        self.start_command = start_command
        
    def run(self):
        self.start_command()
        
class AcceptanceTestModule(Module):
    '''
    Some special configuration of the DI stuff for acceptance tests.
    '''
    
    
    def __init__(self, config_file):
        self.config_file = config_file
        
    def configure(self, binder):
        
        binder.bind(baseinjectorkeys.CONFIG_FILE_KEY, to=self.config_file)
        binder.bind(guiinjectorkeys.MAIN_RUNNER_KEY,
                    ClassProvider(MainRunner), scope=singleton)
        binder.bind(baseinjectorkeys.CreatorProvider,
                    ClassProvider(BasicCreatorProvider), scope=singleton)
        binder.bind(guiinjectorkeys.SETUP_RUNNER_KEY,
                    ClassProvider(SetupRunner), scope=singleton)
        binder.bind(guiinjectorkeys.CHECK_DATABASE_VERSION_KEY,
                    ClassProvider(StartupTaskCheckDatabaseVersion), scope=singleton)
        #binder.bind(guiinjectorkeys.LOGIN_KEY,
        #            ClassProvider(StartupTaskLogin), scope=singleton)
        binder.bind(guiinjectorkeys.POPULATE_WINDOWS_KEY,
                    ClassProvider(StartupTaskPopulateWindows), scope=singleton)

    @provides(guiinjectorkeys.INIT_MESSAGES_KEY, scope=singleton)
    def provide_init_messages(self):
        return [CONF_DOCUMENT_WINDOW_READY, CONF_EVENT_WINDOW_READY]
        

    @provides(guiinjectorkeys.SETUP_TASKS_KEY, scope=singleton)
    @inject(populate_windows=guiinjectorkeys.POPULATE_WINDOWS_KEY)
    def provide_startup_tasks(self, populate_windows):
        return (populate_windows,)

    @provides(guiinjectorkeys.DOCUMENT_MENU_ADDITIONS_KEY, scope=singleton)
    def document_plugins(self):
        return ()

class AcceptanceTestHelpers():
    '''
    Helper class with mostly assertions that need to be mixed in into
    the acceptance test thread class.
    '''
    def get_event(self, entity_id):
        return self.get_entity(entity_id, baseinjectorkeys.EreignisDaoKey)

    def get_document(self, document_id):
        return self.get_entity(document_id, baseinjectorkeys.DokumentDaoKey)

    def get_entity(self, entity_id, dao_key):
        dao = self.injector.get(dao_key)
        return dao.get_by_id(entity_id)

    def assertEquals(self, item1, item2):
        assert(item1 == item2)
        
    def assertTrue(self, expression):
        assert(expression)
        
    def assertFalse(self, expression):
        assert(not expression)

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

class BaseAcceptanceTest(Thread, AcceptanceTestHelpers):
    '''
    The framework for setting up an acceptance test. It initializes a test environment,
    sets up the database, builds the DI container and gets crucial stuff from the
    DI container as properties of the class.
    '''
    
    def __init__(self):
        super().__init__()
        self.gui_initialized = False

        # Build up environment
        self.env = TestEnvironment(mode=MODE_FULL)

        # Initialize dependency injection
        self.injector = Injector([
            AcceptanceTestModule(self.env.config_file_name),
            AlexBaseModule(),
            DaoModule(),
            ServiceModule(),
            PresentersModule(),
            MainWindowsModule(),
            DialogsTkGuiModule(),
            WindowReferencesModule()
            ])
        
        # Set up database
        engine = self.injector.get(baseinjectorkeys.DBEngineKey)
        setup_database_schema(engine)
        load_table_data(tables, engine)
        
        # Get basic gui element
        self.success = False
        self.main_runner = self.injector.get(guiinjectorkeys.MAIN_RUNNER_KEY)
        self.event_window = self.injector.get(guiinjectorkeys.EVENT_WINDOW_KEY)
        self.event_window_presenter = self.injector.get(guiinjectorkeys.EVENT_WINDOW_PRESENTER_KEY)
        self.document_window = self.injector.get(guiinjectorkeys.DOCUMENT_WINDOW_KEY)
        self.document_window_presenter = self.injector.get(guiinjectorkeys.DOCUMENT_WINDOW_PRESENTER_KEY)
        
    def run(self):
        '''
        The threads run class. It waits for the gui to be initalized, then runs
        the test_suite method, that needs to be implemented in the child class.
        '''

        while not self.gui_initialized:
            sleep(1)

        print("Test starts running...")
        print("######################\n")
        try:
            self.test_suite()
            self.success = True
        except:
            pass
        
        if not self.success:
            print("FAILED")
            self.event_window_presenter.quit()
            print("\nAcceptance test failed!")
        else:
            print("\nAcceptance test succeeded!")

    def test_suite(self):
        '''
        Abstract method to overwrite in child classes.
        '''
        
        raise Exception("Overwrite test_suite method in acceptance test class.")
    
    def wait(self):
        '''
        Waits until the gui signals to be idle.
        '''
        
        self.gui_initialized = False
        while not self.gui_initialized:
            sleep(1)

    def start_dialog(self, command):
        '''
        Starts the dialog invoked by the command given as parameter in a new
        thread and waits until the gui becomes idle.
        '''
        
        dialog_starter = DialogStarter(command)
        dialog_starter.start()
        self.wait()
        
    def close_dialog(self, dialog):
        '''
        Presses the first button on the given dialog (which should be the OK
        button), then waits for the gui to become idle again.
        '''
        
        dialog.dialog.invoke(0)
        self.wait()
            
class AcceptanceTestRunner:
    '''
    The runner class for acceptance tests that establishes two threads - one
    for the gui, the other for the tests. The test class given when initializing
    the runner must be an instance of Thread. It also needs a property with the
    instance of the main runner, so this can be started in the main thread.
    '''
    
    def __init__(self, test):
        self.test = test
    
    def run(self):
        """
        Starts the test in a different thread because the gui loop blocks
        this thread. The test thread gets informed when the gui is idle.
        Then the gui_initalized property of the test thread is set to True.
        """
        self.test.start()
        self.test.main_runner.window_manager.root.after_idle(self.mark_gui_initialized) 
        self.test.main_runner.run()
        self.test.join()
        
    def mark_gui_initialized(self):
        '''
        Callback for after_idle in the main loop
        '''
        self.test.gui_initialized = True
        self.test.main_runner.window_manager.root.after(500, self.check_initialized_again)
        
    def check_initialized_again(self):
        '''
        Callback for after in the main loop. It does nothing except when the test
        thread waits again for the gui to be initalized (when starting or closing
        dialogs).
        '''
        if self.test.gui_initialized:
            self.test.main_runner.window_manager.root.after(500, self.check_initialized_again)
        else:
            self.test.main_runner.window_manager.root.after_idle(self.mark_gui_initialized) 
