'''
Created on 31.10.2015

@author: michael
'''
from tkgui.dialogs.abstractdialog import AbstractInputDialog, InputDialogWindow

from tkinter import Label, Tk, Button
import Pmw
from alexpresenters.dialogs.yearselectiondialogpresenter import YearSelectionDialogPresenter
from tkinter.constants import LEFT, END

from tkgui import guiinjectorkeys
from injector import inject
from tkgui.components.alexwidgets import DateEntryFrame

weekdays = (_('MO'), _('TU'), _('WE'), _('TH'), _('FR'), _('SA'), _('SU'))

class YearSelectionDialog(AbstractInputDialog):
    
    @inject
    def __init__(self, presenter: guiinjectorkeys.YEAR_SELECTION_DIALOG_PRESENTER_KEY):
        super().__init__(presenter)
        self.day = None
        self.month = None
        self.day_of_week = None
        self.year_list = []
        self.selected_year = None

    def _init_dialog(self, master, day, month, weekday_shortcut):
        self.day = day
        self.month = month
        self.day_of_week = weekdays.index(weekday_shortcut.upper())
        self.year_list = []
        self.selected_year = None
        
        self.presenter.calculate_year_list()
        if len(self.year_list) == 0:
            return None
        
        self.dialog = InputDialogWindow(master)
        Label(self.dialog.interior(), text="%s:" % _('Please select year')).pack()
        year_list_combo_box = Pmw.ComboBox(self.dialog.interior(), # @UndefinedVariable
                                  selectioncommand=self._on_select,
                                  listbox_width = 20)
        for year in self.year_list:
            year_list_combo_box.insert(END, year)

        year_list_combo_box.pack(padx=5, pady=5)

    def _on_select(self, value):
        self.selected_year = value
        
if __name__=='__main__':
    
    presenter = YearSelectionDialogPresenter()
    dialog = YearSelectionDialog(presenter)
    
    root = Tk()
    date_entry_frame = DateEntryFrame(root)
    date_entry_frame.pack()
    def set_year():
        date_entry_frame.year = dialog.activate(
                            root, 
                            int(date_entry_frame.day), 
                            int(date_entry_frame.month), 
                            date_entry_frame.year)
        
    button = Button(root, text="Start dialog", command=set_year)
    button.pack(side=LEFT)
    button = Button(root, text="Cancel", command=root.quit)
    button.pack(side=LEFT)
    root.mainloop()
