'''
Created on 24.10.2015

@author: michael
'''
import unittest
from tkgui import guiinjectorkeys
from tkgui.components.references.eventcrossreferences import EventCrossReferencesView
from unittest.mock import MagicMock
from alexandriabase import baseinjectorkeys
from alexpresenters import PresentersModule
from alexpresenters.messagebroker import Message, CONF_EVENT_CHANGED,\
    REQ_SET_EVENT
from integration.baseintegrationtest import BaseIntegrationTest


class EventCrossReferencesPresenterTest(BaseIntegrationTest):


    def setUp(self):
        super().setUp()
        self.injector = self.get_injector(PresentersModule())
        self.event_dao = self.injector.get(baseinjectorkeys.EreignisDaoKey)
        self.presenter = self.injector.get(guiinjectorkeys.EVENT_CROSS_REFERENCES_PRESENTER_KEY)
        self.presenter.view = MagicMock(spec=EventCrossReferencesView)
        
    def testReceiveMessage(self):
        
        # Construct message
        event = self.event_dao.get_by_id(1940000001)
        message = Message(CONF_EVENT_CHANGED, event=event)
        
        # Message
        self.presenter.receive_message(message)
        
        # Assert
        self.assertTrue(self.presenter.view.event == event)
        self.assertTrue(len(self.presenter.view.items), 2)
        self.assertIn(self.event_dao.get_by_id(1950000001), self.presenter.view.items)
        self.assertIn(self.event_dao.get_by_id(1960013001), self.presenter.view.items)
        
    def testGotoEvent(self):
        event = self.event_dao.get_by_id(1940000001)
        self.presenter.view.selected_item = event 
        self.presenter.goto_event()
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0].key, REQ_SET_EVENT)
        self.assertEqual(self.received_messages[0].event, event)

    def testGotoEventNothingSelected(self):
        self.presenter.view.selected_item = None # If we wouldn't intialize, we'd get a mock
        self.presenter.goto_event()
        self.assertEqual(len(self.received_messages), 0)

    def testAddNewCrossReference(self):
        
        self.presenter.view.event = self.event_dao.get_by_id(1940000001)
        self.presenter.view.new_cross_reference_event = self.event_dao.get_by_id(1961050101)
        self.presenter.add_new_cross_reference()
        
        # Assert that database has changed
        event_crossreferences_dao = self.injector.get(baseinjectorkeys.EventCrossreferencesDaoKey)
        cross_reference_ids = event_crossreferences_dao.get_cross_references(1940000001)
        self.assertEqual(len(cross_reference_ids), 3)
        self.assertIn(1950000001, cross_reference_ids)
        self.assertIn(1960013001, cross_reference_ids)
        self.assertIn(1961050101, cross_reference_ids)

        # Assert that view has been updated
        self.assertEqual(len(self.presenter.view.items), 3)
        self.assertIn(self.event_dao.get_by_id(1950000001), self.presenter.view.items)
        self.assertIn(self.event_dao.get_by_id(1961050101), self.presenter.view.items)
        self.assertIn(self.event_dao.get_by_id(1960013001), self.presenter.view.items)

    def testAddNewCrossReferenceCancel(self):
        
        self.presenter.view.event = self.event_dao.get_by_id(1940000001)
        self.presenter.view.new_cross_reference_event = None
        self.presenter.add_new_cross_reference()
        
        # Assert that database has not changed
        event_crossreferences_dao = self.injector.get(baseinjectorkeys.EventCrossreferencesDaoKey)
        cross_reference_ids = event_crossreferences_dao.get_cross_references(1940000001)
        self.assertEqual(len(cross_reference_ids), 2)
        self.assertIn(1950000001, cross_reference_ids)
        self.assertIn(1960013001, cross_reference_ids)

        # Assert that view has not changed
        self.assertEqual(len(self.presenter.view.items), 2)
        self.assertIn(self.event_dao.get_by_id(1950000001), self.presenter.view.items)
        self.assertIn(self.event_dao.get_by_id(1960013001), self.presenter.view.items)

    def testDeleteCrossReference(self):
        
        self.presenter.view.event = self.event_dao.get_by_id(1940000001)
        self.presenter.view.selected_item = self.event_dao.get_by_id(1960013001)
        self.presenter.delete_cross_reference()
        
        # Assert that database has changed
        event_crossreferences_dao = self.injector.get(baseinjectorkeys.EventCrossreferencesDaoKey)
        cross_reference_ids = event_crossreferences_dao.get_cross_references(1940000001)
        self.assertEqual(len(cross_reference_ids), 1)
        self.assertEqual(cross_reference_ids[0], 1950000001)

        # Assert that view has been updated
        self.assertEqual(len(self.presenter.view.items), 1)
        self.assertEqual(self.presenter.view.items[0], self.event_dao.get_by_id(1950000001))

    def testDeleteCrossReferenceNothingSelected(self):
        
        self.presenter.view.event = self.event_dao.get_by_id(1940000001)
        self.presenter._update_crossreferences() # Initialize items
        self.presenter.view.selected_item = None # If we wouldn't intialize, we'd get a mock 
        
        self.presenter.delete_cross_reference()
        
        # Assert that database has not changed
        event_crossreferences_dao = self.injector.get(baseinjectorkeys.EventCrossreferencesDaoKey)
        cross_reference_ids = event_crossreferences_dao.get_cross_references(1940000001)

        self.assertEqual(len(cross_reference_ids), 2)
        self.assertIn(1950000001, cross_reference_ids)
        self.assertIn(1960013001, cross_reference_ids)

        # Assert that view is still correct
        self.assertEqual(len(self.presenter.view.items), 2)
        self.assertIn(self.event_dao.get_by_id(1950000001), self.presenter.view.items)
        self.assertIn(self.event_dao.get_by_id(1960013001), self.presenter.view.items)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()