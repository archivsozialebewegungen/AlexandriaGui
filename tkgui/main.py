'''
Created on 07.02.2015

@author: michael
'''
from injector import inject, Injector, Module, ClassProvider, singleton,\
    provides
from alexandriabase import AlexBaseModule, baseinjectorkeys
from alexandriabase.daos import DaoModule
from alexandriabase.services import ServiceModule
from alexpresenters import PresentersModule
from alexpresenters.dialogs.logindialogpresenter import LoginCreatorProvider
from tkgui import guiinjectorkeys
from tkgui.components.references import WindowReferencesModule
from tkgui.dialogs import DialogsTkGuiModule
from tkgui.mainwindows import MainWindowsModule
from alexpresenters.messagebroker import REQ_GOTO_FIRST_DOCUMENT, Message,\
    REQ_GOTO_FIRST_EVENT, CONF_DOCUMENT_WINDOW_READY, CONF_EVENT_WINDOW_READY,\
    REQ_INITIALIZE_MAIN_WINDOWS
from alexpresenters.mainwindows.BaseWindowPresenter import REQ_QUIT
import gettext
from tkinter import TclError
import os
import sys
import Pmw
import logging
import socket
import re
import importlib

class StartupTaskCheckDatabaseVersion():
    
    @inject(message_broker = guiinjectorkeys.MESSAGE_BROKER_KEY,
            database_upgrade_service=baseinjectorkeys.DATABASE_UPGRADE_SERVICE_KEY)
    def __init__(self, message_broker, database_upgrade_service):
        self.message_broker = message_broker
        self.database_upgrade_service = database_upgrade_service
        
    def run(self, root):
        
        if not self.database_upgrade_service.is_update_necessary():
            return True
        dialog = Pmw.MessageDialog(root,  # @UndefinedVariable
            title = _('Database upgrade'),
            message_text = _('Your database needs an upgrade. Do you want to perform it now?'),
            buttons = (_('Yes'), _('No'))
            )
        result = dialog.activate()
        if result == _('No'):
            return False
        
        self.database_upgrade_service.run_update()
        return True

class StartupTaskLogin(object):
    
    @inject(login_dialog=guiinjectorkeys.LOGIN_DIALOG_KEY,
            creator_provider=baseinjectorkeys.CreatorProvider)   
    def __init__(self, login_dialog, creator_provider):
        self.login_dialog=login_dialog
        self.creator_provider=creator_provider
        
    def run(self, root):
        
        self.login_dialog.activate(root)
        if self.creator_provider.creator == None:
            return False
        else:
            return True
            
class StartupTaskPopulateWindows(object):
 
    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY)   
    def __init__(self, message_broker):
        
        self.message_broker = message_broker
        
    def run(self, root):
        
        self.message_broker.send_message(Message(REQ_INITIALIZE_MAIN_WINDOWS))
        self.message_broker.send_message(Message(REQ_GOTO_FIRST_DOCUMENT))
        self.message_broker.send_message(Message(REQ_GOTO_FIRST_EVENT))
        return True

class SetupRunner():
    '''
    This class is used to run certain tasks before the application
    really starts. It is needed to provide login, database upgrades
    etc.
    
    It is started on application start and waits for configured
    messages until it runs the setup tasks defined.
    '''
    
    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY,
            init_messages=guiinjectorkeys.INIT_MESSAGES_KEY,
            setup_tasks=guiinjectorkeys.SETUP_TASKS_KEY)
    def __init__(self, message_broker, init_messages, setup_tasks):

        self.message_broker = message_broker        
        self.message_broker.subscribe(self)
        self.expected_messages = init_messages
        self.received_messages = []
        self.setup_tasks = setup_tasks
        self.root = None
        
    def receive_message(self, message):
        if message in self.expected_messages:
            self.received_messages.append(message)    
    
    def run(self, root):
        self.root = root
        if self.all_messages_received():
            self.run_setup_tasks()
        else:
            self.root.after_idle(lambda: self.run(self.root))
            
    def all_messages_received(self):
        for message in self.expected_messages:
            if message in self.received_messages:
                return True
        return False
    
    def run_setup_tasks(self):
        for task in self.setup_tasks:
            continue_tasks = task.run(self.root)
            if not continue_tasks:
                break
        if not continue_tasks:
            self.message_broker.send_message(Message(REQ_QUIT))
            
class MainRunner:
    
    @inject(
            config=baseinjectorkeys.CONFIG_KEY,
            main_windows=guiinjectorkeys.MAIN_WINDOWS_KEY)
    def __init__(self, config, main_windows):
        '''
        Initializes the whole application. To force the
        initialization of all windows, the main windows
        are injectd and the window manager extracted from
        one of the windows (just injecting the window manager
        won't initalize the windows).
        '''
        self.config = config
        self.window_manager = main_windows[0].window_manager
        
    def run(self):
        '''
        Runs the whole application.
        '''
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.join(self.config.logdir,
                                                   "%s.gui.log" % socket.gethostname()))
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.window_manager.run()

def build_injector():
    '''
    This function allows to build the DI container with
    additional input from the configuration file.
    '''
    
    base_module = AlexBaseModule()
    main_module = MainModule()
    module_list = [base_module,
                   DaoModule(),
                   ServiceModule(),
                   PresentersModule(),
                   MainWindowsModule(),
                   DialogsTkGuiModule(),
                   WindowReferencesModule(),
                   main_module]
    
    config = base_module.get_config(main_module.get_config_file())
    regex = re.compile("(.*)\.(.*)")
    for additional_module in config.additional_modules:
        matcher = regex.match(additional_module)
        class_module = matcher.group(1)
        class_name = matcher.group(2)
        module_class = getattr(importlib.import_module(class_module), class_name)
        module_list.append(module_class())
        
    return Injector(module_list)
        

if __name__ == '__main__':
    
    class MainModule(Module):
        '''
        Initializes the application.
        
        This might be replaced for a special customer installation.
        '''
    
        def configure(self, binder):
            binder.bind(baseinjectorkeys.CreatorProvider,
                        ClassProvider(LoginCreatorProvider), scope=singleton)
            binder.bind(guiinjectorkeys.MAIN_RUNNER_KEY,
                        ClassProvider(MainRunner), scope=singleton)
            binder.bind(guiinjectorkeys.SETUP_RUNNER_KEY,
                        ClassProvider(SetupRunner), scope=singleton)
            binder.bind(guiinjectorkeys.CHECK_DATABASE_VERSION_KEY,
                        ClassProvider(StartupTaskCheckDatabaseVersion), scope=singleton)
            binder.bind(guiinjectorkeys.LOGIN_KEY,
                        ClassProvider(StartupTaskLogin), scope=singleton)
            binder.bind(guiinjectorkeys.POPULATE_WINDOWS_KEY,
                        ClassProvider(StartupTaskPopulateWindows), scope=singleton)
            
        @provides(baseinjectorkeys.CONFIG_FILE_KEY)
        def get_config_file(self):
            config_file = os.environ.get('ALEX_CONFIG')
            if config_file is None:
                config_file = "config.xml"
            return config_file
        
        @provides(guiinjectorkeys.INIT_MESSAGES_KEY, scope=singleton)
        def provide_init_messages(self):
            return [CONF_DOCUMENT_WINDOW_READY, CONF_EVENT_WINDOW_READY]
        
        @provides(guiinjectorkeys.DOCUMENT_MENU_ADDITIONS_KEY, scope=singleton)
        def document_plugins(self, document_pdf_plugin):
            return ()

        @provides(guiinjectorkeys.SETUP_TASKS_KEY, scope=singleton)
        @inject(check_database_version=guiinjectorkeys.CHECK_DATABASE_VERSION_KEY,
                login=guiinjectorkeys.LOGIN_KEY,
                populate_windows=guiinjectorkeys.POPULATE_WINDOWS_KEY)
        def provide_startup_tasks(self, check_database_version, login, populate_windows):
            return [check_database_version, login, populate_windows]
    
    gettext.bindtextdomain('alexandria', 'locale')
    gettext.textdomain('alexandria')
    success = False
    
    try:
        injector = build_injector()
        injector.get(guiinjectorkeys.MAIN_RUNNER_KEY).run()
    except TclError:
        python = sys.executable
        os.execl(python, python, * sys.argv)

