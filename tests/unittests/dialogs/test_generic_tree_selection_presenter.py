'''
Created on 30.11.2016

@author: michael
'''
import unittest
from unittest.mock import MagicMock

from alexpresenters.DialogPresenters import GenericTreeSelectionPresenter


def doNothing():
    
    pass

class GenericTreeSelectionPresenterTest(unittest.TestCase):

    def testSetTreeNeedsOverwriting(self):
        '''
        '''
        generic_presenter = GenericTreeSelectionPresenter()
        try:
            generic_presenter.view = MagicMock()
        except Exception as e:
            self.assertEqual('Please overwrite in child class', "%s" % e)
            expected_exception_thrown = True
        self.assertTrue(expected_exception_thrown,
                        "Expected exception has not been thrown!")
        
    def testSettingReturnValue(self):
        '''
        Tests that the return value in the view object is set
        after ok_action is performed
        '''
        generic_presenter = GenericTreeSelectionPresenter()
        generic_presenter.set_tree = lambda: doNothing
        generic_presenter.view = MagicMock()
        generic_presenter.view.input.entity = "Hello world!"
        
        generic_presenter.ok_action()
        
        self.assertEqual(generic_presenter.view.return_value, "Hello world!")
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()