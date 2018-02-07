'''
Created on 24.10.2015

@author: michael
'''
import unittest
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from unittest.mock import MagicMock
from alexpresenters.MessageBroker import Message, CONF_DOCUMENT_CHANGED,\
    CONF_EVENT_CHANGED, REQ_SET_DOCUMENT, ERROR_MESSAGE
from tkgui.components.references.eventdocumentreferences import EventDocumentReferencesView
from integration.components.references.basereferenceintegrationtest import BaseReferenceIntegrationTest
from ddt import ddt, unpack, data
from alexpresenters.Module import PresentersModule

@ddt
class EventDocumentReferencesPresenterTest(BaseReferenceIntegrationTest):


    def setUp(self):
        super().setUp()
        self.injector = self.get_injector(PresentersModule())
        self.document_dao = self.injector.get(baseinjectorkeys.DOCUMENT_DAO_KEY)
        self.event_dao = self.injector.get(baseinjectorkeys.EVENT_DAO_KEY)
        self.presenter = self.injector.get(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_PRESENTER_KEY)
        self.view = MagicMock(spec=EventDocumentReferencesView)
        self.view.current_document = None
        self.presenter.view = self.view


    def test_receive_message_I(self):
        
        event = self.event_dao.get_by_id(1940000001)
        message = Message(CONF_EVENT_CHANGED, event=event)
        
        self.message_broker = self.injector.get(guiinjectorkeys.MESSAGE_BROKER_KEY)
        self.message_broker.send_message(message)
        
        self.assertEqual(self.view.current_event.id, event.id)

    def test_receive_message_II(self):
        
        self.set_current_event(1940000001)
        self.assertEqual(len(self.view.items), 2)
        
    def test_receive_message_III(self):
        
        message = Message(CONF_EVENT_CHANGED, event=None)
        
        self.message_broker = self.injector.get(guiinjectorkeys.MESSAGE_BROKER_KEY)
        self.message_broker.send_message(message)
        
        self.assertEqual(0, len(self.view.items))

    def test_receive_message_IV(self):
        
        self.message_broker = self.injector.get(guiinjectorkeys.MESSAGE_BROKER_KEY)

        message = Message(CONF_DOCUMENT_CHANGED, document=self.document_dao.get_by_id(1))
        self.message_broker.send_message(message)

        self.assertEqual(1, self.view.current_document.id)
        
        message = Message(CONF_DOCUMENT_CHANGED, document=None)
        self.message_broker.send_message(message)

        self.assertTrue(self.view.current_document is None)

    def test_change_document_I(self):

        self.set_current_event(1940000001)        

        self.presenter.change_document()
        
        self.assertMessage(REQ_SET_DOCUMENT)
        for message in self.received_messages:
            if message.key == REQ_SET_DOCUMENT:
                self.assertEqual(message.document, self.view.selected_item)
        
    def test_change_document_II(self):

        self.set_current_event(1950000001)
        self.view.selected_item = None        
        self.assertEqual(len(self.received_messages), 1)
        self.presenter.change_document()
        # Nothing happend
        self.assertEqual(len(self.received_messages), 1)

    @data([1950000001, 8], [None, 8], [1950000001, None], [None, None])
    @unpack
    def test_add_new_reference(self, event_id, document_id):
        self.set_current_event(event_id)
        self.set_current_document(document_id)
        
        self.assertEqual(0, len(self.view.items))
        
        self.view.new_document_id = 8
        
        self.presenter.reference_document()
        
        event_id = self.presenter.view.current_event.id
        document_id = self.presenter.view.current_document.id
        self.assertFalse(event_id is None)
        self.assertFalse(document_id is None)
        
        self.assertEqual(1, len(self.view.items))

        self.set_current_event(1940000001)

        self.set_current_event(event_id)
        self.assertEqual(1, len(self.view.items))
        
    def test_add_new_reference_no_document_id(self):
        self.set_current_event(1950000001)
        self.assertEqual(0, len(self.view.items))
        
        self.view.new_document_id = None
        self.presenter.reference_document()
        
        self.assertEqual(0, len(self.view.items))

    def test_add_new_reference_illegal_document_id(self):
        self.set_current_event(1950000001)
        self.assertEqual(0, len(self.view.items))
        
        self.view.new_document_id = 85
        self.presenter.reference_document()
        
        self.assertEqual(0, len(self.view.items))
        self.assertMessage(ERROR_MESSAGE)
        self.assertEqual(self.received_messages[-1].message, 'No such document')

    def test_remove_reference(self):
        self.set_current_event(1940000001)
        self.assertEqual(2, len(self.view.items))

        self.view.selected_item = self.document_dao.get_by_id(1)
        self.presenter.remove_document_reference()
        self.view.selected_item = self.document_dao.get_by_id(4)
        self.presenter.remove_document_reference()

        self.assertEqual(0, len(self.view.items))

        self.set_current_event(1950000001)

        self.set_current_event(1940000001)
        self.assertEqual(0, len(self.view.items))

    def test_remove_reference_edge_case(self):
        self.set_current_event(1940000001)
        self.assertEqual(2, len(self.view.items))
        self.view.selected_item = None
        
        self.presenter.remove_document_reference()
        self.assertEqual(2, len(self.view.items))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()