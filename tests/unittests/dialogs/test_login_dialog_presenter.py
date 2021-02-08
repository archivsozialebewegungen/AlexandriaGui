'''
Created on 27.05.2016

@author: michael
'''
import unittest
from unittest.mock import MagicMock

from alexandriabase.domain import Creator
from alexandriabase.services import CreatorService
from alexpresenters.DialogPresenters import LoginDialogPresenter


class TestLoginDialogPresenter(unittest.TestCase):

    def setUp(self):
        self.creator1 = Creator(1)
        self.creator1.name = "Hugo Maier"
        self.creator1.visible = True

        self.creator2 = Creator(2)
        self.creator2.name = "Klara Muller"
        self.creator2.visible = True
        
        self.creators = [self.creator1, self.creator2]

        self.view = MagicMock()
        
        creator_service = MagicMock(spec=CreatorService)
        creator_service.find_all_active_creators.return_value = self.creators

        self.presenter = LoginDialogPresenter(creator_service)
        self.presenter.view = self.view
        
    def test_set_creators(self):
        self.assertEqual(self.view.creators, self.creators)

    def test_selected_creator(self):
        self.view.selected_creator = self.creator1
        self.presenter.ok_action()
        self.assertEqual(self.view.return_value, self.creator1)

    def test_cancel(self):
        self.view.input = None
        self.presenter.cancel_action()
        self.assertEqual(self.view.return_value, None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()