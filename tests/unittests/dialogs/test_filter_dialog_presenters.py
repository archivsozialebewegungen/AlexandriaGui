'''
Created on 22.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from alexandriabase.domain import AlexDate, GenericFilter, DocumentFilter,\
    EventFilter
from alexpresenters.dialogs.yearselectiondialogpresenter import YearSelectionDialogPresenter
from tkgui.dialogs.yearselectiondialog import YearSelectionDialog

import gettext
from alexpresenters.dialogs.filterpresenters import GenericFilterDialogPresenter,\
    DocumentFilterDialogPresenter, EventFilterDialogPresenter
from tkgui.dialogs.filterdialogs import GenericFilterDialog,\
    DocumentFilterDialog, EventFilterDialog
gettext.bindtextdomain('alexandria', 'locale')
gettext.textdomain('alexandria')
_ = gettext.gettext

class GenericFilterDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = GenericFilterDialogPresenter()
        self.view = MagicMock(spec=GenericFilterDialog)
        self.presenter.view = self.view

    def test_assemble_return_value(self):
        
        self.view.searchterms = ['One', 'Two']
        
        self.presenter.assemble_return_value()
        
        self.assertEqual(GenericFilter, self.view.return_value.__class__)
        self.assertEqual(['One', 'Two'], self.view.return_value.searchterms) 

class DocumentFilterDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = DocumentFilterDialogPresenter()
        self.view = MagicMock(spec=DocumentFilterDialog)
        self.presenter.view = self.view

    def test_assemble_return_value(self):
        
        self.view.searchterms = ['One', 'Two']
        self.view.signature = "1.2.III-4"
        
        self.presenter.assemble_return_value()
        
        document_filter = self.view.return_value
        self.assertEqual(DocumentFilter, document_filter.__class__)
        self.assertEqual(['One', 'Two'], document_filter.searchterms) 
        self.assertEqual("1.2.III-4", document_filter.location)
        
class EventFilterDialogPresenterTest(unittest.TestCase):

    def setUp(self):
        self.presenter = EventFilterDialogPresenter()
        self.view = MagicMock(spec=EventFilterDialog)
        self.presenter.view = self.view

    def test_assemble_return_value(self):
        
        self.view.searchterms = ['One', 'Two']
        self.view.earliest_date = AlexDate(1970)
        self.view.latest_date = AlexDate(1980)
        self.view.local_only = True
        self.view.unverified_only = False
        
        self.presenter.assemble_return_value()
        
        event_filter = self.view.return_value
        self.assertEqual(EventFilter, event_filter.__class__)
        self.assertEqual(['One', 'Two'], event_filter.searchterms) 
        self.assertEqual(AlexDate(1970), event_filter.earliest_date)
        self.assertEqual(AlexDate(1980), event_filter.latest_date)
        self.assertTrue(event_filter.local_only)
        self.assertFalse(event_filter.unverified_only)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()