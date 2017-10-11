'''
Created on 07.02.2015

@author: michael
'''
from injector import inject, Injector, Module, ClassProvider, singleton,\
    provider
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
from tkinter import TclError
import os
import sys
import Pmw
import logging
import socket
from tkgui.PluginManager import PluginManager
import time
import threading

class StartupTaskCheckDatabaseVersion():
    
    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 database_upgrade_service: baseinjectorkeys.DATABASE_UPGRADE_SERVICE_KEY):
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
    
    @inject
    def __init__(self,
                 login_dialog: guiinjectorkeys.LOGIN_DIALOG_KEY,
                 creator_provider: baseinjectorkeys.CREATOR_PROVIDER_KEY):
        self.login_dialog=login_dialog
        self.creator_provider=creator_provider
        
    def run(self, root):
        
        self.login_dialog.activate(root)
        if self.creator_provider.creator == None:
            return False
        else:
            return True
            
class StartupTaskPopulateWindows(object):
 
    @inject
    def __init__(self, message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY):
        
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
    
    @inject
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 init_messages: guiinjectorkeys.INIT_MESSAGES_KEY,
                 setup_tasks: guiinjectorkeys.SETUP_TASKS_KEY):

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
    
    @inject
    def __init__(self,
                 config: baseinjectorkeys.CONFIG_KEY,
                 main_windows: guiinjectorkeys.MAIN_WINDOWS_KEY):
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
    
    config = base_module.get_config()
    plugin_manager = PluginManager(config)
    module_list += plugin_manager.get_plugin_modules()
    
    injector = Injector(module_list)
    return injector
        
class MainModule(Module):
    '''
    Initializes the application.
    '''
  
    def configure(self, binder):
        binder.bind(baseinjectorkeys.CREATOR_PROVIDER_KEY,
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
            
    @provider
    @singleton
    def provide_init_messages(self) -> guiinjectorkeys.INIT_MESSAGES_KEY:
        return [CONF_DOCUMENT_WINDOW_READY, CONF_EVENT_WINDOW_READY]
       
    @provider
    @singleton
    @inject
    def provide_startup_tasks(self,
                              check_database_version: guiinjectorkeys.CHECK_DATABASE_VERSION_KEY,
                              login: guiinjectorkeys.LOGIN_KEY,
                              populate_windows: guiinjectorkeys.POPULATE_WINDOWS_KEY) -> guiinjectorkeys.SETUP_TASKS_KEY:
        return [check_database_version, login, populate_windows]

if __name__ == '__main__':
    
#    injector = build_injector()
#    print("%d threads running" % threading.active_count())
#    main_runner = injector.get(guiinjectorkeys.MAIN_RUNNER_KEY)
#    main_runner.run()

    try:
        injector = build_injector()
        main_runner = injector.get(guiinjectorkeys.MAIN_RUNNER_KEY)
        main_runner.run()
    except TclError:
        python = sys.executable
        os.execl(python, python, * sys.argv)

