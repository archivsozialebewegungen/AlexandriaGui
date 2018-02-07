'''
Created on 22.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from alexandriabase.domain import AlexDate
from alexandriabase import _
from alexpresenters.DialogPresenters import DateSelectionDialogPresenter
from tkgui.Dialogs import DateSelectionDialog


class DateSelectionDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = DateSelectionDialogPresenter()
        self.view = MagicMock(spec=DateSelectionDialog)
        self.presenter.view = self.view

    def test_valid_date(self):
        self.view.days = ["1"]
        self.view.months = ["12"]
        self.view.years = ["1960"]
        
        self.presenter.ok_action()
        
        self.assertEqual(AlexDate(1960, 12, 1), self.view.return_value)
        
    def test_invalid_day(self):
        self.view.days = ["32"]
        self.view.months = ["12"]
        self.view.years = ["1960"]

        self.presenter.ok_action()
        
        self.assertEqual(_("Day 32 is out of range (1-31)!"), self.view.errormessage)

    def test_invalid_month(self):
        self.view.days = ["31"]
        self.view.months = ["13"]
        self.view.years = ["1960"]
        
        self.presenter.ok_action()
        
        self.assertEqual("Month 13 is out of range (1-12)!", self.view.errormessage)

    def test_invalid_year(self):
        self.view.days = ["31"]
        self.view.months = ["12"]
        self.view.years = ["10000"]
        
        self.presenter.ok_action()
        
        self.assertEqual(_("Year 10000 is out of range (0-3000)!"), self.view.errormessage)

    def test_illegal_date(self):

        self.view.days = ["31"]
        self.view.months = ["2"]
        self.view.years = ["1970"]
        
        self.presenter.ok_action()
        
        self.assertEqual(_("Illegal date: 31.2.1970!"), self.view.errormessage)

    def test_empty_day_and_month(self):

        self.view.days = [""]
        self.view.months = [""]
        self.view.years = ["1970"]
        
        self.presenter.ok_action()
        
        self.assertEqual(AlexDate(1970), self.view.return_value)

    def test_illegal_day(self):

        self.view.days = ["bla"]
        self.view.months = ["12"]
        self.view.years = ["1970"]
        
        self.presenter.ok_action()
        
        self.assertEqual(_("'bla' is not a valid day!"), self.view.errormessage)

    def test_illegal_month(self):

        self.view.days = ["1"]
        self.view.months = ["bla"]
        self.view.years = ["1970"]
        
        self.presenter.ok_action()
        
        self.assertEqual(_("'bla' is not a valid month!"), self.view.errormessage)

    def test_illegal_year(self):

        self.view.days = ["1"]
        self.view.months = ["12"]
        self.view.years = ["bla"]
        
        self.presenter.ok_action()
        
        self.assertEqual(_("'bla' is not a valid year!"), self.view.errormessage)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()