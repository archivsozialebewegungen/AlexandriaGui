'''
Created on 24.10.2015

@author: michael
'''
import unittest
from alexandriabase.daos.metadata import ALEXANDRIA_METADATA
from alex_test_utils import load_table_data, clear_table_data, TestEnvironment,\
    MODE_SIMPLE, setup_database_schema, drop_database_schema
from injector import Module, Injector, ClassProvider, singleton
from alexandriabase import baseinjectorkeys, AlexBaseModule
from alexandriabase.daos import DaoModule
from alexandriabase.services import ServiceModule
from tkgui import guiinjectorkeys
from daotests import test_base
from alexandriabase.daos.basiccreatorprovider import BasicCreatorProvider
import os
from alexandriabase.domain import Document, DocumentType, Event, AlexDateRange,\
    AlexDate
from alexpresenters.messagebroker import CONF_DOCUMENT_CHANGED, Message,\
    CONF_EVENT_CHANGED, REQ_SAVE_CURRENT_EVENT, REQ_SAVE_CURRENT_DOCUMENT,\
    MessageBroker


class IntegrationTestModule(Module):
            
    def configure(self, binder):

        binder.bind(guiinjectorkeys.MESSAGE_BROKER_KEY,
                    ClassProvider(MessageBroker), scope=singleton)
        
class BaseIntegrationTest(unittest.TestCase):

    '''
    Sets up the database and provides easy access to the injector
    and to messages.
    
    To get the injector in the child class, use the get_injector method
    and provide it with the modules you want to test. This base class also
    loads all modules from AlexandriaBase and the message broker, so you
    need not to specify them.
    
    The class subscribes also to the message broker. To see, which messages
    have been received during the test run, read the property received_messages.
    '''

    def setUp(self):
        self.received_messages = []
        self.engine = None  # Will be set when getting the injector
        self.message_broker = None  # Will be set when getting the injector
        self.env = self.setup_environment()

    def setup_environment(self):
        '''
        You may overwrite this in your test class to receive the
        full integration test environment with data files
        '''
        return TestEnvironment(mode=MODE_SIMPLE)

    def assertMessage(self, message):
        self.assertTrue(message in self.received_messages)


    def receive_message(self, message):
        self.received_messages.append(message)
 
    def get_injector(self, *test_modules):

        essential_modules = (AlexBaseModule(), DaoModule(), ServiceModule(), IntegrationTestModule())
        injector = Injector(essential_modules + test_modules)

        self.engine = injector.get(baseinjectorkeys.DBEngineKey)
        setup_database_schema(self.engine)
        load_table_data(test_base.tables, self.engine)

        self.message_broker = injector.get(guiinjectorkeys.MESSAGE_BROKER_KEY)
        self.message_broker.subscribe(self)

        return injector

    def tearDown(self):
        clear_table_data(test_base.tables, self.engine)
        drop_database_schema(self.engine)
        self.env.cleanup()
