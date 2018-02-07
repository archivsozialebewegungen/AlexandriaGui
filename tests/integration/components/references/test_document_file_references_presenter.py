'''
Created on 24.10.2015

@author: michael
'''
import unittest
from tkgui import guiinjectorkeys
from alexandriabase import baseinjectorkeys
from unittest.mock import MagicMock
from alexpresenters.MessageBroker import Message, CONF_DOCUMENT_CHANGED,\
    ERROR_MESSAGE
from alexpresenters import _
from tkgui.components.references.documentfilereference import DocumentFileReferencesView
from alex_test_utils import TestEnvironment, MODE_FULL
import os
from alexandriabase.base_exceptions import NoSuchEntityException
from alexandriabase.domain import Document
from ddt import ddt, data, unpack
from integration.components.references.basereferenceintegrationtest import BaseReferenceIntegrationTest
from alexpresenters.Module import PresentersModule

@ddt
class DocumentFileReferencesPresenterTest(BaseReferenceIntegrationTest):

    def setUp(self):
        super().setUp()
        self.injector = self.get_injector(PresentersModule())
        self.document_dao = self.injector.get(baseinjectorkeys.DOCUMENT_DAO_KEY)
        self.document_file_info_dao = self.injector.get(baseinjectorkeys.DOCUMENT_FILE_INFO_DAO_KEY)
        self.document_file_manager = self.injector.get(baseinjectorkeys.DOCUMENT_FILE_MANAGER_KEY)
        self.presenter = self.injector.get(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_PRESENTER_KEY)
        self.view = MagicMock(spec=DocumentFileReferencesView)
        self.presenter.view = self.view
        
    def setup_environment(self):
        return TestEnvironment(mode=MODE_FULL)
    
    def test_receive_message(self):
        message = Message(CONF_DOCUMENT_CHANGED, document=self.document_dao.get_last())
        self.message_broker.send_message(message)
        
        self.assertEqual(14, self.view.current_document.id)
        self.assertEqual(1, len(self.view.items))
    
    def test_receive_message_no_document(self):
        message = Message(CONF_DOCUMENT_CHANGED, document=None)
        self.message_broker.send_message(message)
        
        self.assertEqual(None, self.view.current_document)
        self.assertEqual(0, len(self.view.items))

    @data([14, 14], [None, 15])
    @unpack
    def test_working_add(self, document_id, expected_id):
        
        self.view.new_file = self.env.jpg_input_file
        self.set_current_document(document_id)
        
        self.assertTrue(os.path.isfile(self.env.jpg_input_file))
        self.assert_file_info_does_not_exist(15)
            
        self.presenter.add_file()
        
        # Assert that the input file is gone
        self.assertFalse(os.path.isfile(self.env.jpg_input_file))

        # Assert that we have the new info and that a new 
        # document file is where it should be
        file_info = self.document_file_info_dao.get_by_id(15)
        self.assertEqual(expected_id, file_info.document_id)
        self.assertEqual('jpg', file_info.filetype)
        self.assertEqual(400, file_info.resolution)
        file_path = self.document_file_manager.get_file_path(file_info)
        self.assertNotEqual(None, file_path)
        self.assertTrue(os.path.isfile(file_path))
        
    def test_failing_illegal_filetype(self):
        self.view.new_file = self.env.illegal_input_file
        self.view.current_document = self.document_dao.get_last()
        
        self.presenter.add_file()

        self.assertMessage(ERROR_MESSAGE)
        self.assertEqual("File format 'foo' is not supported!",
                         self.received_messages[0].message)

        self.assertTrue(os.path.isfile(self.env.illegal_input_file))
        self.assert_file_info_does_not_exist(15)

    def test_failing_add_wrong_resolution(self):
        self.view.new_file = self.env.tif_input_file
        self.view.current_document = self.document_dao.get_last()
        
        self.presenter.add_file()

        self.assertMessage(ERROR_MESSAGE)
        self.assertEqual("File resolution 72 x 72 is not supported!",
                         self.received_messages[0].message)

        self.assertTrue(os.path.isfile(self.env.tif_input_file))
        self.assert_file_info_does_not_exist(15)
        
    def test_generic_failing(self):
        self.view.new_file = os.path.join(self.env.tmpdir.name, "notexisting.tif")
        self.view.current_document = self.document_dao.get_last()
        
        self.presenter.add_file()

        self.assertMessage(ERROR_MESSAGE)
        self.assertEqual("No such file or directory",
                         self.received_messages[0].message)

        self.assertTrue(os.path.isfile(self.env.illegal_input_file))
        self.assert_file_info_does_not_exist(15)

    def test_utter_failure(self):
        self.view.new_file = Document()
        self.view.current_document = self.document_dao.get_last()
        
        self.presenter.add_file()

        self.assertMessage(ERROR_MESSAGE)
        self.assertEqual(_("Unknown error while adding file"),
                         self.received_messages[0].message)

        self.assertTrue(os.path.isfile(self.env.illegal_input_file))
        self.assert_file_info_does_not_exist(15)

    def test_no_file_selected(self):
        self.view.new_file = None
        self.view.current_document = self.document_dao.get_last()
        
        self.presenter.add_file()

        self.assertEqual(0, len(self.received_messages))
        self.assert_file_info_does_not_exist(15)

    def test_no_current_document(self):
        self.view.new_file = self.env.jpg_input_file
        self.view.current_document = None
        
        self.presenter.add_file()

        self.assertEqual(0, len(self.received_messages))
        self.assert_file_info_does_not_exist(15)
        
    def test_delete_i(self):
        self.generic_deletion_check(self.document_dao.get_by_id(8), 8)

    def test_delete_ii(self):
        self.generic_deletion_check(self.document_dao.get_by_id(8), 9)

    def generic_deletion_check(self, document, info_id):
        message = Message(CONF_DOCUMENT_CHANGED, document=document)
        self.message_broker.send_message(message)

        for item in self.view.items:
            if item.id == info_id:
                self.view.selected_item = item

        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[info_id]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[info_id]))

        self.presenter.remove_file()
        
        self.assertEqual(2, len(self.view.items))
        self.assert_file_info_does_not_exist(info_id)
        self.assertFalse(os.path.isfile("%s" % self.env.file_paths[info_id]))
        self.assertTrue(os.path.isfile("%s.deleted" % self.env.file_paths[info_id]))
        
    def test_delete_iii(self):
        message = Message(CONF_DOCUMENT_CHANGED, document=self.document_dao.get_by_id(8))
        self.message_broker.send_message(message)

        self.view.selected_item = None

        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[8]))
        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[9]))
        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[10]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[8]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[9]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[10]))

        self.presenter.remove_file()
        
        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[8]))
        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[9]))
        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[10]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[8]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[9]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[10]))

        self.assertEqual(3, len(self.view.items))
        
    def test_replace(self):

        self.setup_for_replacement()
        
        # Prepare view for presenter
        self.view.selected_item = self.view.items[1]
        self.view.new_file = self.env.jpg_input_file

        self.presenter.replace_file()
        
        # Assert that the file info is updated
        self.assertEqual(3, len(self.view.items))
        self.assertEqual(10, self.view.items[1].id)
        self.assertEqual(400, self.view.items[1].resolution)
        self.assertEqual('jpg', self.view.items[1].filetype)
        
        info_in_database = self.document_file_info_dao.get_by_id(10)
        self.assertEqual('jpg', info_in_database.filetype)
        
        self.assertFalse(os.path.isfile("%s" % self.env.file_paths[10]))
        self.assertTrue(os.path.isfile("%s.deleted" % self.env.file_paths[10]))
        file_path = self.document_file_manager.get_file_path(info_in_database)
        self.assertNotEqual(None, file_path)
        self.assertTrue(os.path.isfile(file_path))

    def test_replace_fail_i(self):

        self.setup_for_replacement()
        
        # Prepare view for presenter
        self.view.selected_item = None
        self.view.new_file = self.env.jpg_input_file

        self.presenter.replace_file()
        
        self.assert_no_changes()
        
    def test_replace_fail_ii(self):

        self.setup_for_replacement()
        
        # Prepare view for presenter
        self.view.selected_item = self.view.items[1]
        self.view.new_file = None

        self.presenter.replace_file()
        
        self.assert_no_changes()

    def test_show_file(self):

        message = Message(CONF_DOCUMENT_CHANGED, document=self.document_dao.get_last())
        self.message_broker.send_message(message)

        self.view.selected_item = self.view.items[0]        
        self.view.show_file = None
        
        self.presenter.show_file()
        
        self.assertEqual(self.env.file_paths[14], self.view.show_file)
        
    def test_show_file2(self):
        '''
        Test with missing file. Should produce error message
        '''

        message = Message(CONF_DOCUMENT_CHANGED, document=self.document_dao.get_last())
        self.message_broker.send_message(message)

        self.view.selected_item = self.view.items[0]        
        self.view.show_file = None
        
        os.unlink(self.env.file_paths[14])
        
        self.presenter.show_file()
        
        self.assertMessage(ERROR_MESSAGE)

    def test_show_file_no_selection(self):
        
        self.view.show_file = None
        self.view.selected_item = None
        
        self.presenter.show_file()
        
        self.assertEqual(None, self.view.show_file)

    def assert_no_changes(self):
        self.assertEqual(3, len(self.view.items))
        self.assertEqual(10, self.view.items[1].id)
        self.assertEqual(400, self.view.items[1].resolution)
        self.assertEqual('tif', self.view.items[1].filetype)
        
        info_in_database = self.document_file_info_dao.get_by_id(9)
        self.assertEqual('tif', info_in_database.filetype)
        
        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[9]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[9]))
        file_path = self.document_file_manager.get_file_path(info_in_database)
        self.assertEqual(self.env.file_paths[9], file_path)

    def setup_for_replacement(self):

        
        # Init view
        message = Message(CONF_DOCUMENT_CHANGED, document=self.document_dao.get_by_id(8))
        self.message_broker.send_message(message)
        
        # Assert before        
        self.assertEqual(3, len(self.view.items))
        self.assertEqual(10, self.view.items[1].id)
        self.assertEqual(400, self.view.items[1].resolution)
        self.assertEqual('tif', self.view.items[1].filetype)
        self.assertTrue(os.path.isfile("%s" % self.env.file_paths[9]))
        self.assertFalse(os.path.isfile("%s.deleted" % self.env.file_paths[9]))

    def assert_file_info_does_not_exist(self, id):
        exception_thrown = False
        try:
            self.document_file_info_dao.get_by_id(id)
        except NoSuchEntityException:
            exception_thrown = True
        self.assertTrue(exception_thrown)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()