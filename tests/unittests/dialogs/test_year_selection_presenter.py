'''
Created on 22.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock

from alexpresenters.DialogPresenters import YearSelectionDialogPresenter
from tkgui.Dialogs import YearSelectionDialog


class YearSelectionDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = YearSelectionDialogPresenter()
        self.view = MagicMock(spec=YearSelectionDialog)
        self.view.day = 29
        self.view.month = 2
        self.view.day_of_week = 0
        self.presenter.view = self.view

    def test_list_calculation(self):
        
        expected = ['1960', '1988', '2016', '2044']
        self.assertEqual(expected, self.view.year_list)
        
    def test_value_assembly(self):
        
        self.view.selected_year = '1960'
        
        self.presenter.ok_action()
        
        self.assertEqual('1960', self.view.return_value)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()