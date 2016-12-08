'''
Created on 22.11.2015

@author: michael
'''

import unittest
from tkgui import guiinjectorkeys
from alexpresenters import PresentersModule
from integration.baseintegrationtest import BaseIntegrationTest
from alexandriabase import baseinjectorkeys
from alexandriabase.domain import AlexDateRange, AlexDate, EventFilter, Event,\
    alex_date_from_key
from alexpresenters.mainwindows.BaseWindowPresenter import REQ_QUIT
from alexandriabase.base_exceptions import NoSuchEntityException
from alexpresenters.messagebroker import REQ_SET_EVENT, Message,\
    REQ_GOTO_FIRST_EVENT, CONF_EVENT_WINDOW_READY, REQ_SAVE_CURRENT_EVENT,\
    CONF_EVENT_CHANGED
from unittest.mock import MagicMock
from tkgui.mainwindows.EventWindow import EventWindow

class ViewStub():
    
    def __init__(self):
        self.entity = None
        self.filter_expression = None
        self._entity_has_changed = False
        
    def entity_has_changed(self):
        return self._entity_has_changed

class EventWindowsTests(BaseIntegrationTest):


    def setUp(self):
        super().setUp()
        self.injector = self.get_injector(PresentersModule())
        self.event_window_presenter = self.injector.get(guiinjectorkeys.EVENT_WINDOW_PRESENTER_KEY)
        self.event_service = self.injector.get(baseinjectorkeys.EventServiceKey)
        #self.view = ViewStub()
        self.view = MagicMock(spec=EventWindow)
        self.view.entity = None
        self.view.filter_expression = None
        self.view.entity_has_changed.return_value = False
        
        self.event_window_presenter.view = self.view;


    def tearDown(self):
        pass

    def testReceiveMessage(self):
        
        self.view.entity = Event()
        self.view.entity.daterange = AlexDateRange(AlexDate(1936), None)
        self.view.entity_has_changed.return_value = True
        
        self.message_broker.send_message(Message(REQ_SAVE_CURRENT_EVENT))
        
        self.assertMessage(REQ_SAVE_CURRENT_EVENT)
        self.assertMessage(CONF_EVENT_CHANGED)

    def testGotoFirst(self):
        self.event_window_presenter.goto_first()
        self.assertEqual(self.view.entity.id, 1940000001)
        
    def testGotoLast(self):
        self.event_window_presenter.goto_last()
        self.assertEqual(self.view.entity.id, 1961050101)

    def testGotoNextI(self):
        self.view.entity = self.event_service.get_by_id(1950000001)
        self.event_window_presenter.goto_next()
        self.assertEqual(self.view.entity.id, 1960013001)
        
    def testGotoNextII(self):
        # Edgecase
        self.view.entity = self.event_service.get_by_id(1961050101)
        self.event_window_presenter.goto_next()
        self.assertEqual(self.view.entity.id, 1940000001)
        
    def testGotoNextIII(self):
        # Edgecase
        self.view.entity = None
        self.event_window_presenter.goto_next()
        self.assertEqual(self.view.entity, None)
        
    def testGotoPreviousI(self):
        self.view.entity = self.event_service.get_by_id(1950000001)
        self.event_window_presenter.goto_previous()
        self.assertEqual(self.view.entity.id, 1940000001)

    def testGotoPreviousII(self):
        self.view.entity = self.event_service.get_by_id(1940000001)
        self.event_window_presenter.goto_previous()
        self.assertEqual(self.view.entity.id, 1961050101)
        
    def testGotoPreviousIII(self):
        self.view.entity = None
        self.event_window_presenter.goto_previous()
        self.assertEqual(self.view.entity, None)

    def testGotoRecordI(self):
        self.event_window_presenter.goto_first()
        self.view.record_id_selection = alex_date_from_key(1949122401)
        self.event_window_presenter.goto_record()
        self.assertEqual(self.view.entity.id, 1950000001)

    def testGotoRecordII(self):
        self.event_window_presenter.goto_first()
        self.view.record_id_selection = None
        self.event_window_presenter.goto_record()
        self.assertEqual(self.view.entity.id, 1940000001)

    def testSavingI(self):
        self.event_window_presenter.goto_first()
        self.view.entity.description = "Totally new description"
        self.view.entity_has_changed.return_value = True
        self.event_window_presenter.goto_last()
        entity = self.event_service.get_by_id(1940000001)
        self.assertEqual(entity.description, "Totally new description")

    def testSavingII(self):
        self.event_window_presenter.goto_first()
        self.view.entity.daterange = AlexDateRange(AlexDate(1950), None)
        self.view.entity_has_changed.return_value = True
        self.event_window_presenter.goto_last()
        exception_raised = False
        try:
            self.event_service.get_by_id(1940000001)
        except NoSuchEntityException:
            exception_raised = True
        self.assertTrue(exception_raised)
        entity = self.event_service.get_by_id(1950000002)
        self.assertEqual(entity.description, "Erstes Ereignis")
        
    def testToggleFilterI(self):
        self.view.new_filter = EventFilter()
        self.view.new_filter.searchterms = ["Erstes"]
        
        self.event_window_presenter.toggle_filter()
        self.event_window_presenter.goto_last()
        
        self.assertEqual(self.view.entity.id, 1940000001)

    def testToggleFilterII(self):
        self.view.new_filter = EventFilter()
        self.view.new_filter.searchterms = ["Does not match any record"]
        
        self.event_window_presenter.toggle_filter()
        self.event_window_presenter.goto_last()
        
        self.assertEqual(self.view.entity, None)

    def testToggleFilterIII(self):
        self.view.filter_expression = "Does not matter"
        
        self.event_window_presenter.toggle_filter()

        self.assertEqual(self.view.filter_expression, None)
        
    def testToggleFilterIV(self):
        self.view.filter_expression = None
        self.view.new_filter = None
        
        self.event_window_presenter.toggle_filter()

        self.assertEqual(self.view.filter_expression, None)
        
    def testCreateNewI(self):
        
        self.view.new_date_range = AlexDateRange(AlexDate(1950), None)
        self.view.existing_new_event = Event()
        self.view.existing_new_event.daterange = self.view.new_date_range
        self.event_window_presenter.create_new()
        
        self.assertEqual(self.view.entity.daterange, AlexDateRange(AlexDate(1950), None))
        self.assertEqual(self.view.entity.id, None)
        self.assertEqual(self.view.entity.description, '')
        
    def testCreateNewII(self):
        
        self.view.new_date_range = None
        self.event_window_presenter.goto_first()
        self.event_window_presenter.create_new()
        
        self.assertEqual(self.view.entity.daterange, AlexDateRange(AlexDate(1940), None))
        self.assertEqual(self.view.entity.id, 1940000001)
        self.assertEqual(self.view.entity.description, "Erstes Ereignis")

    def testCreateNewIII(self):
        
        self.view.new_date_range = AlexDateRange(AlexDate(1936), None)
        self.view.existing_new_event = None
        self.view.entity_has_changed = MagicMock(side_effect = [False, False, True, False])
        self.event_window_presenter.create_new()
        
        self.event_window_presenter.goto_last()
        self.event_window_presenter.goto_first()
        self.assertEqual(self.view.entity.daterange, AlexDateRange(AlexDate(1936), None))
        self.assertEqual(self.view.entity.id, 1936000001)
        self.assertEqual(self.view.entity.description, "")

    def testDeleteI(self):
        # Plain and simple deletion
        self.view.entity = self.event_service.get_by_id(1940000001)
        
        self.event_window_presenter.delete()
        
        self.assertEqual(self.view.entity.id, 1950000001)
        
    def testDeleteII(self):
        # Nothing to delete
        self.view.entity = None
        
        self.event_window_presenter.delete()
        
        self.assertEqual(self.view.entity, None)
        
    def testDeleteIII(self):
        # Entity is not yet persisted
        self.view.entity = Event()
        
        self.event_window_presenter.delete()
        
        self.assertEqual(self.view.entity, self.event_service.get_last(None))
        
    def testDeleteIV(self):
        # Delete all
        for i in range(0,4):  # @UnusedVariable
            self.event_window_presenter.goto_first()
            self.event_window_presenter.delete()
            
        self.assertEqual(self.view.entity, None)
        
    def testChangeEventDateI(self):
        
        exception_raised = False
        try:
            self.event_service.get_by_id(1950000002)
        except NoSuchEntityException:
            exception_raised = True
        self.assertTrue(exception_raised)

        self.view.entity = self.event_service.get_by_id(1940000001)
        self.view.new_date_range = AlexDateRange(AlexDate(1950), None)
        
        self.event_window_presenter.change_event_date()
        self.view._entity_has_changed = True
        
        self.event_window_presenter.goto_last() # Saves the entity
        self.event_window_presenter.goto_first() # Our entity is no longer the first entity
        self.event_window_presenter.goto_next()
        
        self.assertEqual(self.view.entity.id, 1950000002)
        self.assertEqual(self.event_service.get_by_id(1950000002), self.view.entity)

    def testChangeEventDateII(self):
        
        self.view.entity = self.event_service.get_by_id(1940000001)
        self.view.new_date_range = None
        
        self.event_window_presenter.change_event_date()
        self.view._entity_has_changed = True
        
        self.event_window_presenter.goto_last() # Saves the entity
        self.event_window_presenter.goto_first()

        self.assertEqual(self.view.entity.id, 1940000001)
        self.assertEqual(self.event_service.get_by_id(1940000001), self.view.entity)
        
    def test_change_event_by_message(self):
        
        self.event_window_presenter.goto_last()
        self.assertEqual(self.view.entity.id, 1961050101)

        event = self.event_service.get_by_id(1940000001)
        message = Message(REQ_SET_EVENT, event=event)
        self.event_window_presenter.receive_message(message)
        
        self.assertEqual(self.view.entity.id, 1940000001)
        
        
    def testQuit(self):
        self.assertEqual(len(self.received_messages), 0)
        self.event_window_presenter.quit()
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], REQ_QUIT)
        

    def test_set_event_by_message(self):
        self.message_broker.send_message(Message(REQ_GOTO_FIRST_EVENT))
        self.assertEqual(self.event_window_presenter.view.entity.id, 1940000001)
        
    def test_signal_window_ready(self):
        
        self.event_window_presenter.signal_window_ready()
        self.assertMessage(CONF_EVENT_WINDOW_READY)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()