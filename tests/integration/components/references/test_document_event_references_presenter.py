'''
Created on 24.10.2015

@author: michael
'''
import unittest
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from unittest.mock import MagicMock
from alexpresenters.MessageBroker import Message, CONF_DOCUMENT_CHANGED,\
    CONF_EVENT_CHANGED, REQ_SET_EVENT
from tkgui.components.references.documenteventreferences import DocumentEventReferencesView
from ddt import ddt, data, unpack
from integration.components.references.basereferenceintegrationtest import BaseReferenceIntegrationTest
from alexpresenters.Module import PresentersModule

@ddt
class DocumentEventReferencesPresenterTest(BaseReferenceIntegrationTest):

    def setUp(self):
        super().setUp()
        self.injector = self.get_injector(PresentersModule())
        self.document_dao = self.injector.get(baseinjectorkeys.DOCUMENT_DAO_KEY)
        self.event_dao = self.injector.get(baseinjectorkeys.EVENT_DAO_KEY)
        self.presenter = self.injector.get(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_PRESENTER_KEY)
        self.view = MagicMock(spec=DocumentEventReferencesView)
        self.view.current_event = None
        self.presenter.view = self.view

    def test_receive_message_I(self):
        
        event = self.event_dao.get_by_id(1940000001)
        message = Message(CONF_EVENT_CHANGED, event=event)
        
        self.message_broker = self.injector.get(guiinjectorkeys.MESSAGE_BROKER_KEY)
        self.message_broker.send_message(message)
        
        self.assertEqual(self.view.current_event.id, event.id)

    def test_receive_message_II(self):
        
        self.set_current_document(1)
        self.assertEqual(len(self.view.items), 1)
        
    def test_receive_message_III(self):
        
        message = Message(CONF_DOCUMENT_CHANGED, document=None)
        
        self.message_broker = self.injector.get(guiinjectorkeys.MESSAGE_BROKER_KEY)
        self.message_broker.send_message(message)
        
        self.assertEqual(0, len(self.view.items))

    def test_change_event_I(self):

        self.set_current_document(1)        

        self.presenter.change_event()
        
        self.assertMessage(REQ_SET_EVENT)
        for message in self.received_messages:
            if message.key == REQ_SET_EVENT:
                self.assertEqual(message.event, self.view.selected_item)
        
    def test_change_event_II(self):

        self.set_current_document(8)
        self.view.selected_item = None        
        self.assertEqual(len(self.received_messages), 1)
        self.presenter.change_event()
        # Nothing happend
        self.assertEqual(len(self.received_messages), 1)

    @data([1940000001, 8], [None, 8], [1940000001, None], [None, None])
    @unpack
    def test_add_new_reference(self, event_id, document_id):
        
        self.set_current_document(document_id)
        self.set_current_event(event_id)
        
        self.assertEqual(0, len(self.view.items))
        
        self.view.reference_event = self.view.current_event
        
        self.presenter.reference_event()
        
        document_id = self.view.current_document.id
        event_id = self.view.current_event.id
        self.assertFalse(document_id is None)
        self.assertFalse(event_id is None)
        
        
        self.assertEqual(1, len(self.view.items))

        self.set_current_document(1)

        self.set_current_document(document_id)
        
        self.assertEqual(1, len(self.view.items))
        
    def test_add_new_reference_edge_case(self):
        self.set_current_document(8)
        self.assertEqual(0, len(self.view.items))
        
        self.view.reference_event = None
        self.presenter.reference_event()
        
        self.assertEqual(0, len(self.view.items))

    def test_remove_reference(self):
        self.set_current_document(1)
        self.assertEqual(1, len(self.view.items))
        self.view.selected_item = self.event_dao.get_by_id(1940000001)
        
        self.presenter.remove_event_reference()
        self.assertEqual(0, len(self.view.items))

        self.set_current_document(8)

        self.set_current_document(1)
        self.assertEqual(0, len(self.view.items))

    def test_remove_reference_edge_case(self):
        self.set_current_document(8)
        self.assertEqual(0, len(self.view.items))
        self.view.selected_item = None
        
        self.presenter.remove_event_reference()
        self.assertEqual(0, len(self.view.items))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()