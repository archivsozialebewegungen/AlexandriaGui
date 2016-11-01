'''
Created on 31.10.2015

@author: michael
'''
from datetime import date
from alexpresenters.dialogs.abstractdialogpresenter import AbstractInputDialogPresenter

class YearSelectionDialogPresenter(AbstractInputDialogPresenter):
    '''
    Does the stuff for selecting a year for an incomplete
    date where just the day, the month and the weekday is known
    '''

    def calculate_year_list(self):
        year_list = []
        for year in range(1945, 2050):
            test_date = None
            try:
                test_date = date(year, self.view.month, self.view.day)
            except ValueError:
                pass
            if test_date != None and test_date.weekday() == self.view.day_of_week:
                year_list.append("%d" % year)
        self.view.year_list = year_list
        
    def assemble_return_value(self):

        self.view.return_value = self.view.selected_year
