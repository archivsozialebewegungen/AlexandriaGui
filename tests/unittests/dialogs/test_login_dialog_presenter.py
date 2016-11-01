'''
Created on 27.05.2016

@author: michael
'''
import unittest
from unittest.mock import MagicMock
from alexpresenters.dialogs.logindialogpresenter import LoginCreatorProvider,\
    LoginDialogPresenter
from alexandriabase.services.creatorservice import CreatorService
from alexandriabase.domain import Creator


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
        self.creator_service = MagicMock(spec=CreatorService)
        self.login_creator_provider = LoginCreatorProvider()
        self.presenter = LoginDialogPresenter(self.creator_service,
                                              self.login_creator_provider)
        self.presenter.view = self.view
        
        
    def test_set_creators(self):
        self.creator_service.find_all_active_creators.return_value = self.creators
        self.presenter.set_creators()
        self.assertEqual(self.view.creators, self.creators)

    def test_selected_creator(self):
        self.view.input = self.creator1
        self.presenter.assemble_return_value()
        self.assertTrue(self.view.return_value)
        self.assertEqual(self.login_creator_provider.creator, self.creator1)

    def test_no_selected_creator(self):
        self.view.input = None
        self.presenter.assemble_return_value()
        self.assertFalse(self.view.return_value)
        self.assertEqual(self.login_creator_provider.creator, None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()