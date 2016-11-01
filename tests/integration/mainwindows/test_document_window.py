'''
Created on 22.11.2015

@author: michael
'''

import unittest
from tkgui import guiinjectorkeys
from alexpresenters import PresentersModule
from integration.baseintegrationtest import BaseIntegrationTest
from alexandriabase import baseinjectorkeys
from alexandriabase.domain import Document, DocumentFilter
from alexpresenters.mainwindows.BaseWindowPresenter import REQ_QUIT
import os
from alex_test_utils import TestEnvironment, MODE_FULL
from alexpresenters.messagebroker import REQ_SET_DOCUMENT, Message,\
    REQ_GOTO_FIRST_DOCUMENT, CONF_DOCUMENT_WINDOW_READY

class ViewStub():
    
    def __init__(self):
        self.entity = None
        self.filter_expression = None
        self._entity_has_changed = False
        
    def entity_has_changed(self):
        return self._entity_has_changed

class DocumentWindowsTests(BaseIntegrationTest):


    def setUp(self):
        super().setUp()
        self.injector = self.get_injector(PresentersModule())
        self.document_window_presenter = self.injector.get(guiinjectorkeys.DOCUMENT_WINDOW_PRESENTER_KEY)
        self.document_service = self.injector.get(baseinjectorkeys.DocumentServiceKey)
        self.message_broker = self.injector.get(guiinjectorkeys.MESSAGE_BROKER_KEY)
        self.view = ViewStub()
        self.document_window_presenter.view = self.view;

    def setup_environment(self):
        return TestEnvironment(mode=MODE_FULL)

    def tearDown(self):
        pass


    def testGotoFirst(self):
        self.document_window_presenter.goto_first()
        self.assertEqual(self.view.entity.id, 1)
        
    def testGotoLast(self):
        self.document_window_presenter.goto_last()
        self.assertEqual(self.view.entity.id, 14)

    def testGotoNextI(self):
        self.view.entity = self.document_service.get_by_id(4)
        self.document_window_presenter.goto_next()
        self.assertEqual(self.view.entity.id, 8)
        
    def testGotoNextII(self):
        # Edgecase
        self.view.entity = self.document_service.get_by_id(14)
        self.document_window_presenter.goto_next()
        self.assertEqual(self.view.entity.id, 1)
        
    def testGotoNextIII(self):
        # Edgecase
        self.view.entity = None
        self.document_window_presenter.goto_next()
        self.assertEqual(self.view.entity, None)
        
    def testGotoPreviousI(self):
        self.view.entity = self.document_service.get_by_id(4)
        self.document_window_presenter.goto_previous()
        self.assertEqual(self.view.entity.id, 1)

    def testGotoPreviousII(self):
        self.view.entity = self.document_service.get_by_id(1)
        self.document_window_presenter.goto_previous()
        self.assertEqual(self.view.entity.id, 14)
        
    def testGotoPreviousIII(self):
        self.view.entity = None
        self.document_window_presenter.goto_previous()
        self.assertEqual(self.view.entity, None)

    def testGotoRecordI(self):
        self.document_window_presenter.goto_first()
        self.view.record_id_selection = 4
        self.document_window_presenter.goto_record()
        self.assertEqual(self.view.entity.id, 4)

    def testGotoRecordII(self):
        self.document_window_presenter.goto_first()
        self.view.record_id_selection = None
        self.document_window_presenter.goto_record()
        self.assertEqual(self.view.entity.id, 1)

    def testSavingI(self):
        self.document_window_presenter.goto_first()
        self.view.entity.description = "Totally new description"
        self.view._entity_has_changed = True
        self.document_window_presenter.goto_last()
        self.assertNotEqual(self.view.entity.description, "Totally new description")
        entity = self.document_service.get_by_id(1)
        self.assertEqual(entity.description, "Totally new description")

    def testToggleFilterI(self):
        self.view.new_filter = DocumentFilter()
        self.view.new_filter.searchterms = ["Erstes"]
        
        self.document_window_presenter.toggle_filter()
        self.document_window_presenter.goto_last()
        
        self.assertEqual(self.view.entity.id, 1)

    def testToggleFilterII(self):
        self.view.new_filter = DocumentFilter()
        self.view.new_filter.searchterms = ["Does not match any record"]
        
        self.document_window_presenter.toggle_filter()
        self.document_window_presenter.goto_last()
        
        self.assertEqual(self.view.entity, None)

    def testToggleFilterIII(self):
        self.view.filter_expression = "Does not matter"
        
        self.document_window_presenter.toggle_filter()

        self.assertEqual(self.view.filter_expression, None)
        
    def testToggleFilterIV(self):
        self.view.filter_expression = None
        self.view.new_filter = None
        
        self.document_window_presenter.toggle_filter()

        self.assertEqual(self.view.filter_expression, None)
        
    def testCreateNewI(self):
        
        self.document_window_presenter.create_new()
        
        self.assertEqual(self.view.entity.id, None)
        self.assertEqual(self.view.entity.description, '')
        self.assertEqual(self.view.entity.condition, '')
        self.assertEqual(self.view.entity.keywords, '')
      
    def testDeleteI(self):
        
        # Plain and simple deletion
        entity = self.document_service.get_by_id(8)
        file_infos = self.document_service.get_file_infos_for_document(entity)
        self.assertEqual(len(file_infos), 3)
        
        for i in range(8,11):
            self.assertTrue(os.path.isfile(self.env.file_paths[i]))
            self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[i]))

        self.view.entity = entity
        self.document_window_presenter.delete()
        self.assertEqual(self.view.entity.id, 4)

        file_infos = self.document_service.get_file_infos_for_document(entity)
        self.assertEqual(len(file_infos), 0)
        
        for i in range(8,11):
            self.assertFalse(os.path.isfile(self.env.file_paths[i]))
            self.assertTrue(os.path.isfile("%s.deleted" % self.env.file_paths[i]))
        
    def testDeleteII(self):
        # Nothing to delete
        self.view.entity = None
        
        self.document_window_presenter.delete()
        
        self.assertEqual(self.view.entity, None)
        
    def testDeleteIII(self):
        # Entity is not yet persisted
        self.view.entity = Document()
        
        self.document_window_presenter.delete()
        
        self.assertEqual(self.view.entity, self.document_service.get_last(None))
        
    def testDeleteIV(self):
        # Delete all
        for i in range(0, 7):  # @UnusedVariable
            self.document_window_presenter.goto_first()
            self.document_window_presenter.delete()
            
        self.assertEqual(self.view.entity, None)
        
    def testQuit(self):
        self.assertEqual(len(self.received_messages), 0)
        self.document_window_presenter.quit()
        self.assertEqual(len(self.received_messages), 1)
        self.assertMessage(REQ_QUIT)
        
    def test_set_document_by_message(self):
        document = self.document_service.get_by_id(8)
        self.message_broker.send_message(Message(REQ_GOTO_FIRST_DOCUMENT))
        self.assertEqual(self.document_window_presenter.view.entity.id, 1)
        self.message_broker.send_message(Message(REQ_SET_DOCUMENT, document=document))
        self.assertEqual(self.document_window_presenter.view.entity.id, 8)
        
    def test_signal_window_ready(self):
        
        self.document_window_presenter.signal_window_ready()
        self.assertMessage(CONF_DOCUMENT_WINDOW_READY)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()