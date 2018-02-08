'''
Created on 01.01.2018

@author: michael
'''
from datetime import date
from alexandriabase.domain import AlexDate, InvalidDateException, AlexDateRange,\
    DocumentFilter, EventFilter, GenericFilter
from injector import inject
from alexandriabase import baseinjectorkeys
from alexpresenters import _

class AbstractInputDialogPresenter(object):
    '''
    Class that defines the expected minimal interface of a dialog
    presenter.
    For more information see the documentation in AbstractInputDialog.
    '''
    
    def __init__(self):
        self._view = None
    
    def cancel_action(self):
        '''
        Default behaviour: The activate method of the dialog
        will return None
        '''
        self._view.return_value = None
        
    def ok_action(self):
        '''
        Should set the return_value property of self._view
        '''
        raise Exception("Please overwrite in child class.")
    
    def _set_view(self, view):
        '''
        Override this if you have to set some properties on the view.
        '''
        self._view = view
        
    def _get_view(self):
        '''
        Returns the view object
        '''
        return self._view

    # The lambda allows overwriting in sub classes
    view = property(_get_view, lambda self, v: self._set_view(v))    

class GenericInputDialogPresenter(AbstractInputDialogPresenter):
    '''
    classdocs
    '''

    def ok_action(self):
        
        self._view.return_value = self._view.input
        
    def yes_action(self):
        
        self._view.return_value = True
        
    def no_action(self):
        
        self._view.return_value = False
        
class YearSelectionDialogPresenter(AbstractInputDialogPresenter):
    '''
    Does the stuff for selecting a year for an incomplete
    date where just the day, the month and the weekday is known
    '''

    def _set_view(self, view):
        self._view = view
        year_list = []
        for year in range(1945, 2050):
            test_date = None
            try:
                test_date = date(year, self._view.month, self._view.day)
            except ValueError:
                pass
            if test_date != None and test_date.weekday() == self._view.day_of_week:
                year_list.append("%d" % year)
        self._view.year_list = year_list
        
    def ok_action(self):

        self.view.return_value = self.view.selected_year

class DateSelectionDialogPresenter(AbstractInputDialogPresenter):

    def ok_action(self):
        try:
            (day, month, year) = self._basic_input_conversion(0)
        except Exception as e:
            return

        # Leave further input validation to the AlexDate class
        try:
            self._view.return_value = AlexDate(year, month, day)
        except InvalidDateException as e:
            self._view.errormessage = e.args[0]

    def _basic_input_conversion(self, entry_index):
        days = self._view.days
        months = self._view.months
        years = self._view.years
        day = self._validate_day_input(days[entry_index])
        month = self._validate_month_input(months[entry_index])
        year = self._validate_year_input(years[entry_index])
        return (day, month, year)
        
    def _validate_day_input(self, day):
        if day == '':
            return None
        try:
            return int(day)
        except ValueError:
            self._view.errormessage = _("'%s' is not a valid day!") % day
            raise Exception
            
    def _validate_month_input(self, month):
        if month == '':
            return None
        try:
            return int(month)
        except ValueError:
            self._view.errormessage = _("'%s' is not a valid month!") % month
            raise Exception

    def _validate_year_input(self, year):
        try:
            return int(year)
        except ValueError:
            self._view.errormessage = _("'%s' is not a valid year!") % year
            raise Exception

class EventIdSelectionDialogPresenter(DateSelectionDialogPresenter):

    def ok_action(self):
        try:
            (day, month, year) = self._basic_input_conversion(0)
        except Exception as e:
            return

        # Leave further input validation to the AlexDate class
        try:
            date = AlexDate(year, month, day)
        except InvalidDateException as e:
            self._view.errormessage = e.args[0]
            return

        self._view.return_value = date.as_key(1)

class DateRangeSelectionDialogPresenter(DateSelectionDialogPresenter):
    '''
    classdocs
    '''
    def ok_action(self):
        
        self._view.return_value = self._fetch_return_value()
        
    def _fetch_return_value(self):
        try:
            (start_day, start_month, start_year) = self._basic_input_conversion(0)
        except Exception as e:
            # Errormessage is already set
            return None

        try:
            start_date = AlexDate(start_year, start_month, start_day)
        except InvalidDateException as e:
            self._view.errormessage = e.args[0]
            return None

        if self._view.years[1] == '':
            return AlexDateRange(start_date, None)
        try:
            (end_day, end_month, end_year) = self._basic_input_conversion(1)
        except Exception as e:
            # Errormessage is already set
            return None
        
        try:
            end_date = AlexDate(end_year, end_month, end_day)
        except InvalidDateException as e:
            self._view.errormessage = e.args[0]
            return None
        
        return AlexDateRange(start_date, end_date)

class DocumentIdSelectionDialogPresenter(GenericInputDialogPresenter):
    '''
    A simple presenter for an integer input
    '''

    def ok_action(self):
        id_as_string = self._view.input
        try:
            self._view.return_value = int(id_as_string)
        except ValueError:
            self._view.return_value = None
            
class EventSelectionPresenter(AbstractInputDialogPresenter):
    '''
    Presenter for the event selection wizard
    '''    
    @inject
    def __init__(self, event_service: baseinjectorkeys.EVENT_SERVICE_KEY):
        self.event_service = event_service
        self.exclude_list = []
    
    def update_event_list(self):
        '''
        Sets the eventlist on the second page of the wizard.
        '''
        selected_date = self._view.date
        if not selected_date:
            self._view.event_list = []
        else:
            self._view.event_list = self._get_events_for_date(selected_date)
            
    def _get_events_for_date(self, date):
        '''
        Helper method to fetch events from service and clean up
        the resulting list. The events not wanted must be included
        in the exclude_list property of the class.
        '''
        raw_list = self.event_service.get_events_for_date(date)
        clean_list = []
        for event in raw_list:
            if event in self.exclude_list:
                continue
            clean_list.append(event)
        return clean_list

    def ok_action(self):
        
        self._view.return_value = self.view.input

class GenericTreeSelectionPresenter(AbstractInputDialogPresenter):
    
    def _set_view(self, view):
        super()._set_view(view)    
        self.set_tree()
        
    def set_tree(self):
        raise Exception('Please overwrite in child class')

    def ok_action(self):
        if self._view.input == None:
            return
        self._view.return_value = self._view.input.entity

class EventTypeSelectionPresenter(GenericTreeSelectionPresenter):
    
    @inject
    def __init__(self, event_service: baseinjectorkeys.EVENT_SERVICE_KEY):
        super().__init__()
        self.event_service = event_service
        
    def set_tree(self):
        self._view.tree = self.event_service.get_event_type_tree()

class GenericFilterDialogPresenter(AbstractInputDialogPresenter):
    
    def ok_action(self):
        self._view.return_value = self._build_filter_object()
    
    def _build_filter_object(self):
        filter_object = self._new_filter_object()
        filter_object.searchterms = self._view.searchterms
        return filter_object
    
    def _new_filter_object(self):
        return GenericFilter()
    
class DocumentFilterDialogPresenter(GenericFilterDialogPresenter):
    
    def _build_filter_object(self):
        filter_object = super()._build_filter_object()
        filter_object.signature = self._view.signature
        return filter_object
        
    def _new_filter_object(self):
        return DocumentFilter()

class EventFilterDialogPresenter(GenericFilterDialogPresenter):
    
    def _build_filter_object(self):
        filter_object = super()._build_filter_object()
        filter_object.earliest_date = self._view.earliest_date
        filter_object.latest_date = self._view.latest_date
        filter_object.local_only = self._view.local_only
        filter_object.unverified_only = self._view.unverified_only
        return filter_object

    def _new_filter_object(self):
        return EventFilter()
    
class LoginCreatorProvider(object):
    
    def __init__(self, creator=None):
        self.creator = creator

class LoginDialogPresenter(object):
    '''
    classdocs
    '''

    @inject
    def __init__(self,
                 creator_service: baseinjectorkeys.CREATOR_SERVICE_KEY):
        '''
        Constructor
        '''
        self.creator_service = creator_service
        self._view = None
        
    def _init_view(self, view):
        
        self._view = view
        self._view.creators = self.creator_service.find_all_active_creators()
        
    def ok_action(self):

        self._view.return_value = self._view.selected_creator
    
    def cancel_action(self):

        self._view.return_value = None

    view = property(None, _init_view)
