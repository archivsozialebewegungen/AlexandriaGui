'''
Created on 30.11.2016

@author: michael
'''
import unittest
from alexpresenters.dialogs.eventconfirmationpresenter import EventConfirmationPresenter
from unittest.mock import MagicMock
from alexandriabase.services.eventservice import EventService
from tkgui.dialogs.event_confirmation_dialog import EventConfirmationDialog
from alexandriabase.domain import Event, AlexDate


class EventConfirmationPresenterTest(unittest.TestCase):


    def setUp(self):
        self.service_mock = MagicMock(spec=EventService)
        self.view = MagicMock(spec=EventConfirmationDialog)
        self.event_confirmation_presenter = EventConfirmationPresenter(self.service_mock)
        self.event_confirmation_presenter.view = self.view

    def testName(self):
        self.service_mock.get_events_for_date.return_value = (Event(1940010100), Event(1940010101))
        self.view.date = AlexDate(1940, 1, 1)
        self.event_confirmation_presenter.set_event_list()
        self.assertEqual(2, len(self.view.event_list))
        self.assertEqual(1940010100, self.view.event_list[0].id)
        self.assertEqual(1940010101, self.view.event_list[1].id)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()