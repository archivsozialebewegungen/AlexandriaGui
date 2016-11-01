'''
Created on 22.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock, call
from alexandriabase.domain import AlexDateRange
from tkgui.dialogs.dateselectiondialog import DateRangeSelectionDialog
from alexpresenters.dialogs.daterangeselectiondialogpresenter import DateRangeSelectionDialogPresenter


class DateRangeSelectionDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = DateRangeSelectionDialogPresenter()
        self.view = MagicMock(spec=DateRangeSelectionDialog)
        self.presenter.view = self.view

    def test_single_date(self):
        
        self.view.days = ["1", ""]
        self.view.months = ["12", ""]
        self.view.years = ["1960", ""]
        
        self.presenter.assemble_return_value()
        
        self.assertEqual(AlexDateRange(1960120100, None), self.view.return_value)
        
    def test_invalid_start_input(self):
        
        self.view.days = ["bla", ""]
        self.view.months = ["12", ""]
        self.view.years = ["1960", ""]
        
        self.presenter.assemble_return_value()
                
        self.assertEqual(None, self.view.return_value)
        self.assertEqual("'bla' is not a valid day!", self.view.errormessage)

    def test_illegal_start_date(self):
        
        self.view.days = ["31", ""]
        self.view.months = ["11", ""]
        self.view.years = ["1960", ""]
        
        self.presenter.assemble_return_value()
        
        self.assertEqual(None, self.view.return_value)
        self.assertEqual("Illegal date: 31.11.1960!", self.view.errormessage)

    def test_invalid_end_input(self):
        
        self.view.days = ["1", "bla"]
        self.view.months = ["12", ""]
        self.view.years = ["1960", "1961"]
        
        self.presenter.assemble_return_value()
        
        self.assertEqual(None, self.view.return_value)
        self.assertEqual("'bla' is not a valid day!", self.view.errormessage)

    def test_illegal_end_date(self):
        
        self.view.days = ["1", "31"]
        self.view.months = ["12", "11"]
        self.view.years = ["1960", "1961"]
        
        self.presenter.assemble_return_value()
        
        self.assertEqual(None, self.view.return_value)
        self.assertEqual("Illegal date: 31.11.1961!", self.view.errormessage)

    def test_range(self):
        
        self.view.days = ["1", "31"]
        self.view.months = ["12", "1"]
        self.view.years = ["1960", "1961"]
        
        self.presenter.assemble_return_value()
        
        self.assertEqual(AlexDateRange(1960120100, 1961013100), self.view.return_value)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()