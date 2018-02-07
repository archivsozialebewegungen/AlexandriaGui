'''
Created on 27.05.2016

@author: michael
'''
import unittest
from unittest.mock import MagicMock, call, ANY
from alexpresenters.MainWindowPresenters import BaseWindowPresenter


class TestBaseWindowPresenter(unittest.TestCase):


    def test_save_new_entry_before_postprocessors(self):
        entity = MagicMock()
        entity.id = None
        entity_service = self.run_with_entity(entity)
        self.assertEqual(entity_service.mock_calls,
                         [call.save(ANY), call.save(ANY)]) 

    def test_update_existing_entry_before_postprocessors(self):
        entity = MagicMock()
        entity.id = 1
        entity_service = self.run_with_entity(entity)
        self.assertEqual(entity_service.mock_calls,
                         [call.save(entity)]) 
        
    def run_with_entity(self, entity):
        entity_service = MagicMock()
        message_broker = MagicMock()
        presenter = BaseWindowPresenter(message_broker, entity_service, [])
        presenter.view = MagicMock()
        presenter.view.entity = entity
        presenter.view.entity_has_changed.return_value = True
        
        presenter._save_if_necessary()
        
        return entity_service
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()