'''
Created on 22.10.2015

@author: michael
'''
import unittest
from tkgui.dialogs.eventselectiondialog import EventSelectionWizard
from unittest.mock import MagicMock
from tkgui import guiinjectorkeys
from alexandriabase.domain import AlexDate
from alexpresenters import PresentersModule
from integration.baseintegrationtest import BaseIntegrationTest


class EventSelectionDialogPresenterTest(BaseIntegrationTest):

    def setUp(self):
        super().setUp()
        injector = self.get_injector(PresentersModule())
        self.presenter = injector.get(guiinjectorkeys.EVENT_SELECTION_DIALOG_PRESENTER_KEY)
        self.presenter.view = MagicMock(spec=EventSelectionWizard)

    def testGetEventsForDate(self):
        events = self.presenter._get_events_for_date(AlexDate(1950))
        self.assertEqual(len(events), 1)
        self.assertEqual("%s" % events[0], "1950: Zweites Ereignis")
        self.presenter.exclude_list = events;
        events = self.presenter._get_events_for_date(AlexDate(1950))
        self.assertEqual(len(events), 0)

    def testUpdateEventList1(self):
        self.presenter.view.date = AlexDate(1950)
        self.presenter.update_event_list()
        self.assertEqual(len(self.presenter.view.event_list), 1)
        self.assertEqual("%s" % self.presenter.view.event_list[0], "1950: Zweites Ereignis")
        

    def testUpdateEventList2(self):
        self.presenter.view.date = None
        self.presenter.update_event_list()
        self.assertEqual(len(self.presenter.view.event_list), 0)
        
    def test_close(self):
        self.presenter.close()
        self.presenter.view.close.assert_called_once_with()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()