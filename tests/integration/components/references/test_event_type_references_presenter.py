'''
Created on 24.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from tkgui import guiinjectorkeys
from tkgui.components.references.documentfilereference import DocumentFileReferencesView
from alexandriabase import baseinjectorkeys
from alexandriabase.domain import EventTypeIdentifier, \
    Event, AlexDateRange, AlexDate
from alexpresenters.messagebroker import Message,  CONF_EVENT_CHANGED,\
    REQ_SAVE_CURRENT_EVENT
from alexpresenters import PresentersModule
from integration.baseintegrationtest import BaseIntegrationTest
from ddt import ddt, data, unpack

@ddt
class EventTypeReferencesPresenterTest(BaseIntegrationTest):

    existing_event = Event(1940000001)
    non_existing_event = Event()
    non_existing_event.daterange = AlexDateRange(AlexDate(1930), None)

    def setUp(self):
        super().setUp()
        self.injector = self.get_injector(PresentersModule())
        self.event_service = self.injector.get(baseinjectorkeys.EventServiceKey)
        self.event_type_dao = self.injector.get(baseinjectorkeys.EventTypeDaoKey)
        self.presenter = self.injector.get(guiinjectorkeys.EVENT_TYPE_REFERENCES_PRESENTER_KEY)
        self.view = MagicMock(spec=DocumentFileReferencesView)
        self.presenter.view = self.view
    
    def receive_message(self, message):
        BaseIntegrationTest.receive_message(self, message)
        if message.key == REQ_SAVE_CURRENT_EVENT:
            self.event_service.save(self.view.current_event)
    
    @data([1940000001, 2], [1950000001, 1], [1961050101, 0])
    @unpack    
    def test_receive_message_1(self, event_id, number_of_references):
        '''
        Assert that the event types are set on event changes.
        '''
        message = Message(CONF_EVENT_CHANGED, event=self.event_service.get_by_id(event_id))
        self.message_broker.send_message(message)
        self.assertEqual(number_of_references, len(self.view.items))
                
    def test_load_event_types(self):
        '''
        Just an additional test when there is now event set. Can't be done via
        message.
        '''
        self.presenter._load_event_types(None)
        self.assertEqual(0, len(self.view.items))
        
    @data([existing_event, 3], [non_existing_event, 1])
    @unpack
    def test_add_event_type(self, event, number_of_references):

        message = Message(CONF_EVENT_CHANGED, event=event)
        self.message_broker.send_message(message)

        self.view.new_event_type = self.event_type_dao.get_by_id(EventTypeIdentifier(3,2))

        self.presenter.add_event_type_reference()

        self.assertEqual(number_of_references, len(self.event_service.get_event_types(event)))
    
    def test_add_event_type_2(self):
        '''
        Trying to readd already added type
        '''

        event = self.event_service.get_by_id(1940000001)
        event_type = self.event_type_dao.get_by_id(EventTypeIdentifier(5,2))
        message = Message(CONF_EVENT_CHANGED, event=event)
        self.message_broker.send_message(message)

        self.view.new_event_type = event_type

        self.assertEqual(2, len(self.event_service.get_event_types(event)))

        self.presenter.add_event_type_reference()

        self.assertEqual(2, len(self.event_service.get_event_types(event)))

    def test_add_event_type_3(self):
        '''
        Test when no event type is selected
        '''

        event = self.event_service.get_by_id(1940000001)
        message = Message(CONF_EVENT_CHANGED, event=event)
        self.message_broker.send_message(message)

        self.view.new_event_type = None

        self.assertEqual(2, len(self.event_service.get_event_types(event)))

        self.presenter.add_event_type_reference()

        self.assertEqual(2, len(self.event_service.get_event_types(event)))


    def test_remove_event_type(self):
        
        event = self.event_service.get_by_id(1940000001)
        event_type = self.event_type_dao.get_by_id(EventTypeIdentifier(5,2))
        message = Message(CONF_EVENT_CHANGED, event=event)
        self.message_broker.send_message(message)

        self.view.selected_item = event_type

        self.assertEqual(2, len(self.event_service.get_event_types(event)))

        self.presenter.remove_event_type_reference()

        self.assertEqual(1, len(self.event_service.get_event_types(event)))
        
    def test_remove_event_type_2(self):
        '''
        Test with no type selected.
        '''
        event = self.event_service.get_by_id(1940000001)
        message = Message(CONF_EVENT_CHANGED, event=event)
        self.message_broker.send_message(message)

        self.view.selected_item = None

        self.assertEqual(2, len(self.event_service.get_event_types(event)))

        self.presenter.remove_event_type_reference()

        self.assertEqual(2, len(self.event_service.get_event_types(event)))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()