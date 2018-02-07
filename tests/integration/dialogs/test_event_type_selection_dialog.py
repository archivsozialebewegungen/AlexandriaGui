'''
Created on 22.10.2015

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from tkgui import guiinjectorkeys
from alexandriabase.domain import Tree
from alexpresenters.Module import PresentersModule
from integration.baseintegrationtest import BaseIntegrationTest
from tkgui.Dialogs import EventTypeSelectionDialog


class EventTypeSelectionDialogPresenterTest(BaseIntegrationTest):

    def setUp(self):
        super().setUp()
        injector = self.get_injector(PresentersModule())
        self.presenter = injector.get(guiinjectorkeys.EVENT_TYPE_SELECTION_PRESENTER_KEY)
        self.presenter.view = MagicMock(spec=EventTypeSelectionDialog)

    def testGetEventsForDate(self):
        self.presenter.set_tree()
        self.assertTrue(isinstance(self.presenter.view.tree, Tree))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()