'''
Created on 09.01.2016

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from tkgui.Dialogs import DocumentIdSelectionDialog
from alexpresenters.DialogPresenters import DocumentIdSelectionDialogPresenter


class TestDocumentIdSelection(unittest.TestCase):

    def setUp(self):
        self.view = MagicMock(spec=DocumentIdSelectionDialog)
        self.presenter = DocumentIdSelectionDialogPresenter()
        self.presenter.view = self.view 
        

    def test_with_integer(self):
        self.view.input = "42"
        self.presenter.ok_action()
        self.assertEqual(42, self.view.return_value)
        
    def test_with_non_integer(self):
        self.view.input = "foo"
        self.presenter.ok_action()
        self.assertEqual(None, self.view.return_value)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testN']
    unittest.main()