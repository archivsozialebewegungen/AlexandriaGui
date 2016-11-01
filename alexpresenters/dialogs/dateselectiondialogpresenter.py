'''
Created on 01.11.2015

@author: michael
'''
from alexpresenters.dialogs.abstractdialogpresenter import AbstractInputDialogPresenter
from alexandriabase.domain import InvalidDateException, AlexDate

import gettext

gettext.bindtextdomain('alexandria', 'locale')
gettext.textdomain('alexandria')
_ = gettext.gettext

class DateSelectionDialogPresenter(AbstractInputDialogPresenter):

    def assemble_return_value(self):
        try:
            (day, month, year) = self._basic_input_conversion(0)
        except Exception as e:
            return

        # Leave further input validation to the AlexDate class
        try:
            self.view.return_value = AlexDate(year, month, day)
        except InvalidDateException as e:
            self.view.errormessage = e.args[0]

    def _basic_input_conversion(self, entry_index):
        days = self.view.days
        months = self.view.months
        years = self.view.years
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
            self.view.errormessage = _("'%s' is not a valid day!") % day
            raise Exception
            
    def _validate_month_input(self, month):
        if month == '':
            return None
        try:
            return int(month)
        except ValueError:
            self.view.errormessage = _("'%s' is not a valid month!") % month
            raise Exception

    def _validate_year_input(self, year):
        try:
            return int(year)
        except ValueError:
            self.view.errormessage = _("'%s' is not a valid year!") % year
            raise Exception
