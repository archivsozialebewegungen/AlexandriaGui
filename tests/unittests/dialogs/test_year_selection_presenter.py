'''
Created on 22.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from alexandriabase.domain import AlexDate
from alexpresenters.dialogs.yearselectiondialogpresenter import YearSelectionDialogPresenter
from tkgui.dialogs.yearselectiondialog import YearSelectionDialog

import gettext
gettext.bindtextdomain('alexandria', 'locale')
gettext.textdomain('alexandria')
_ = gettext.gettext

class YearSelectionDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = YearSelectionDialogPresenter()
        self.view = MagicMock(spec=YearSelectionDialog)
        self.presenter.view = self.view

    def test_list_calculation(self):
        
        expected = ['1960', '1988', '2016', '2044']
        self.view.day = 29
        self.view.month = 2
        self.view.day_of_week = 0
        self.presenter.calculate_year_list()
        self.assertEqual(expected, self.view.year_list)
        
    def test_value_assembly(self):
        
        self.view.selected_year = '1960'
        
        self.presenter.assemble_return_value()
        
        self.assertEqual('1960', self.view.return_value)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()