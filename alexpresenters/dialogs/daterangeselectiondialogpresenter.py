'''
Created on 21.11.2015

@author: michael
'''
from alexpresenters.dialogs.dateselectiondialogpresenter import DateSelectionDialogPresenter
from alexandriabase.domain import AlexDate, InvalidDateException, AlexDateRange

class DateRangeSelectionDialogPresenter(DateSelectionDialogPresenter):
    '''
    classdocs
    '''
    def assemble_return_value(self):
        
        self.view.return_value = self._fetch_return_value()
        
    def _fetch_return_value(self):
        try:
            (start_day, start_month, start_year) = self._basic_input_conversion(0)
        except Exception as e:
            # Errormessage is already set
            return None

        try:
            start_date = AlexDate(start_year, start_month, start_day)
        except InvalidDateException as e:
            self.view.errormessage = e.args[0]
            return None

        if self.view.years[1] == '':
            return AlexDateRange(start_date, None)
        try:
            (end_day, end_month, end_year) = self._basic_input_conversion(1)
        except Exception as e:
            # Errormessage is already set
            return None
        
        try:
            end_date = AlexDate(end_year, end_month, end_day)
        except InvalidDateException as e:
            self.view.errormessage = e.args[0]
            return None
        
        return AlexDateRange(start_date, end_date)

        