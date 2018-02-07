'''
Created on 22.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from alexandriabase.domain import AlexDateRange
from alexpresenters.DialogPresenters import DateRangeSelectionDialogPresenter
from tkgui.Dialogs import DateRangeSelectionDialog
from alexpresenters import _


class DateRangeSelectionDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = DateRangeSelectionDialogPresenter()
        self.view = MagicMock(spec=DateRangeSelectionDialog)
        self.presenter.view = self.view

    def test_single_date(self):
        
        self.view.days = ["1", ""]
        self.view.months = ["12", ""]
        self.view.years = ["1960", ""]
        
        self.presenter.ok_action()
        
        self.assertEqual(AlexDateRange(1960120100, None), self.view.return_value)
        
    def test_invalid_start_input(self):
        
        self.view.days = ["bla", ""]
        self.view.months = ["12", ""]
        self.view.years = ["1960", ""]
        
        self.presenter.ok_action()
                
        self.assertEqual(None, self.view.return_value)
        self.assertEqual(_("'%s' is not a valid day!") % 'bla', self.view.errormessage)

    def test_illegal_start_date(self):
        
        self.view.days = ["31", ""]
        self.view.months = ["11", ""]
        self.view.years = ["1960", ""]
        
        self.presenter.ok_action()
        
        self.assertEqual(None, self.view.return_value)
        self.assertEqual("Illegal date: 31.11.1960!", self.view.errormessage)

    def test_invalid_end_input(self):
        
        self.view.days = ["1", "bla"]
        self.view.months = ["12", ""]
        self.view.years = ["1960", "1961"]
        
        self.presenter.ok_action()
        
        self.assertEqual(None, self.view.return_value)
        self.assertEqual(_("'%s' is not a valid day!") % 'bla', self.view.errormessage)

    def test_illegal_end_date(self):
        
        self.view.days = ["1", "31"]
        self.view.months = ["12", "11"]
        self.view.years = ["1960", "1961"]
        
        self.presenter.ok_action()
        
        self.assertEqual(None, self.view.return_value)
        self.assertEqual("Illegal date: 31.11.1961!", self.view.errormessage)

    def test_range(self):
        
        self.view.days = ["1", "31"]
        self.view.months = ["12", "1"]
        self.view.years = ["1960", "1961"]
        
        self.presenter.ok_action()
        
        self.assertEqual(AlexDateRange(1960120100, 1961013100), self.view.return_value)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()