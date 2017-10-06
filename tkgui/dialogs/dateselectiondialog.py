'''
Created on 01.11.2015

@author: michael
'''
from tkgui.dialogs.abstractdialog import AbstractInputDialog, InputDialogWindow
from tkgui.dialogs.yearselectiondialog import weekdays, YearSelectionDialog
from alexpresenters.dialogs.dateselectiondialogpresenter import DateSelectionDialogPresenter
from tkinter import Tk, Button, Label
from tkinter.constants import TOP, LEFT
from alexpresenters.dialogs.yearselectiondialogpresenter import YearSelectionDialogPresenter
from tkgui.components.alexwidgets import AlexLabel, DateEntryFrame
from alexpresenters.dialogs.daterangeselectiondialogpresenter \
    import DateRangeSelectionDialogPresenter
from tkgui import guiinjectorkeys
from injector import inject

class DateSelectionDialog(AbstractInputDialog):
    '''
    Dialog class to select an AlexDate object. When entering a
    weekday instead of a year and day and month are already set
    a year selection dialog is started.
    '''

    def __init__(self, presenter, yearselectiondialog, number_of_entries=1):
        self.date_entry = []
        self.number_of_entries = number_of_entries
        super().__init__(presenter)
        self.yearselectiondialog = yearselectiondialog

    def _init_dialog(self, master):
        # pylint: disable=no-member
        if self.dialog is not None:
            for entry in self.date_entry:
                entry.day = ''
                entry.month = ''
                entry.year = ''
            return 
        self.dialog = InputDialogWindow(master)
        for input_field in range(0, self.number_of_entries):
            date_entry = DateEntryFrame(self.dialog.interior())
            date_entry.day_entry.bind('<KeyRelease>',
                                      lambda event, i=input_field, f='day': self._on_change(event, i, f))
            date_entry.month_entry.bind('<KeyRelease>',
                                        lambda event, i=input_field, f='month': self._on_change(event, i, f))
            date_entry.year_entry.bind('<KeyRelease>',
                                       lambda event, i=input_field, f='year': self._on_change(event, i, f))
            date_entry.pack(padx=10)
            self.date_entry.append(date_entry)
        empty_label = Label(self.dialog.interior())
        empty_label.pack()

    def _on_change(self, event, index, field):
        '''
        Pops up the year selection dialog if we have a day, a month and a weekday
        '''
        self._check_for_weekday_to_year(index)
        if field == 'day':
            self._shift_focus_from_day(index)
        if field == 'month':
            self._shift_focus_from_month(index)
        if field == 'year':
            self._shift_focus_from_year(index)
    
    def _pad_two_digit_year(self, index):
        try:
            year = int(self.date_entry[index].year)
        except ValueError:
            return
        if year <= 45:
            self.date_entry[index].year = year + 2000
        if year > 45 and year < 100:
            self.date_entry[index].year = year + 1900
            
    def _shift_focus_from_day(self, index):
        try:
            day = int(self.date_entry[index].day)
        except ValueError:
            return
        if day == 0 or day > 3:
            self.date_entry[index].month_entry.focus_set()
        
    def _shift_focus_from_month(self, index):
        try:
            month = int(self.date_entry[index].month)
        except ValueError:
            return
        if month == 0 or month > 1:
            self.date_entry[index].year_entry.focus_set()

    def _shift_focus_from_year(self, index):
        if index == len(self.date_entry) - 1:
            return
        try:
            year = int(self.date_entry[index].year)
        except ValueError:
            return
        if year > 999:
            self.date_entry[index+1].day_entry.focus_set()

    def _check_for_weekday_to_year(self, index):
        # pylint: disable=unused-argument
        search_for_year = True
        try:
            day = int(self.date_entry[index].day)
            month = int(self.date_entry[index].month)
            weekday = self.date_entry[index].year
            weekdays.index(weekday.upper())
        except ValueError:
            search_for_year = False
        if search_for_year:
            self.date_entry[index].year = self.yearselectiondialog.activate(
                self.dialog._hull,
                day,
                month,
                weekday)
    
    def _dialog_close(self, button):
        for index in range(0, self.number_of_entries):
            self._pad_two_digit_year(index)
        super()._dialog_close(button)
        
    def _get_days(self):
        days = []
        for entry in self.date_entry:
            days.append(entry.day)
        return days
    
    def _set_days(self, days):
        for i in range(0, self.number_of_entries):
            self.date_entry[i].day = days[i]

    def _get_months(self):
        months = []
        for entry in self.date_entry:
            months.append(entry.month)
        return months

    def _set_months(self, months):
        for i in range(0, self.number_of_entries):
            self.date_entry[i].month = months[i]

    def _get_years(self):
        years = []
        for entry in self.date_entry:
            years.append(entry.year)
        return years

    def _set_years(self, years):
        for i in range(0, self.number_of_entries):
            self.date_entry[i].year = years[i]

    days = property(_get_days, _set_days)
    months = property(_get_months, _set_months)
    years = property(_get_years, _set_years)

class SimpleDateSelectionDialog(DateSelectionDialog):
    '''
    Selects a date.
    '''

    @inject
    def __init__(self, presenter: guiinjectorkeys.DATE_SELECTION_DIALOG_PRESENTER_KEY,
            yearselectiondialog: guiinjectorkeys.YEAR_SELECTION_DIALOG_KEY):
        super().__init__(presenter, yearselectiondialog, 1)

class DateRangeSelectionDialog(DateSelectionDialog):
    '''
    Selects a date range.
    '''

    @inject
    def __init__(self, presenter: guiinjectorkeys.DATERANGE_SELECTION_DIALOG_PRESENTER_KEY,
            yearselectiondialog: guiinjectorkeys.YEAR_SELECTION_DIALOG_KEY):
        super().__init__(presenter, yearselectiondialog, 2)

