'''
Created on 22.10.2015

@author: michael
'''
import unittest
from alexpresenters.DialogPresenters import AbstractInputDialogPresenter

class YearSelectionDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = AbstractInputDialogPresenter()

    def test_assemble_return_value(self):
        
        expected_exception = False
        try:
            self.presenter.assemble_return_value()
        except:
            expected_exception = True
        self.assertTrue(expected_exception)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()