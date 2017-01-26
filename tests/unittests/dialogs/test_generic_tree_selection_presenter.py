'''
Created on 30.11.2016

@author: michael
'''
import unittest
from alexpresenters.dialogs.generic_tree_selection_presenter import GenericTreeSelectionPresenter
from unittest.mock import MagicMock


class GenericTreeSelectionPresenterTest(unittest.TestCase):


    def testAssembleReturnValue(self):
        generic_presenter = GenericTreeSelectionPresenter()
        generic_presenter.view = MagicMock()
        generic_presenter.view.input.entity = "Hello world!"
        
        generic_presenter.assemble_return_value()
        
        self.assertEqual(generic_presenter.view.return_value, "Hello world!")
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()