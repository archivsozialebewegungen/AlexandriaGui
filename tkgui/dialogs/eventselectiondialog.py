'''
Created on 03.10.2015

@author: michael
'''
import Pmw

from tkgui.dialogs.wizard import Wizard
from injector import inject
from tkinter import Frame, Label, TOP, END, BOTH
from tkgui import guiinjectorkeys
from tkgui.components.alexwidgets import AlexDateEntry

class EventSelectionDialog:
    
    @inject(presenter=guiinjectorkeys.EVENT_SELECTION_DIALOG_PRESENTER_KEY)
    def __init__(self, presenter):
        
        self.presenter = presenter
        self.wizard = None
        
    def activate(self, master, default_event=None, exclude_list = []):
        
        self.presenter.exclude_list = exclude_list
        default_date = None
        if default_event is not None:
            default_date = default_event.daterange.start_date
        wizard = EventSelectionWizard(master, self.presenter, default_date=default_date)
        return wizard.selected_event

class EventSelectionWizard(Wizard):
    
    def __init__(self, master, presenter, default_date=None):
        
        self.selected_event = None
        self.date_entry = None
        self.default_date = default_date
        self._event_list = []

        super().__init__(master, presenter, number_of_pages=2)
        # Make dialog modal
        self.grab_set()
        self.minsize(350, 250)
        self._add_all_content()
        self._add_actions()
        # Stop processing in caller
        self.wait_window(self)
        


    def _add_all_content(self):
        self._add_date_entry_content()
        self._add_page1_content()
        
    def _add_date_entry_content(self):
        date_entry_frame = Frame(self.page(0))
        self.add_page_body(date_entry_frame)
        self.date_entry = AlexDateEntry(parent=date_entry_frame,
                                           label=_("Please enter the event date:"),
                                           labelwidth=25)
        if self.default_date is not None:
            self.date_entry.set(self.default_date)
        self.date_entry.pack(side=TOP)
    
    def _add_page1_content(self):
        event_selection_frame = Frame(self.page(1))
        self.add_page_body(event_selection_frame)
        Label(event_selection_frame, text=_("Please select an event:")).pack(side=TOP)
        self.event_list_box = Pmw.ScrolledListBox(event_selection_frame)  # @UndefinedVariable
        self.event_list_box.pack(fill=BOTH)
            
    def _add_actions(self):
        self.actions[1] = self.presenter.update_event_list
        
    def _get_event_list(self):
        return self._event_list
    
    def _set_event_list(self, event_list):
        self._event_list = event_list
        self.event_list_box.delete(0, self.event_list_box.size())
        for event in event_list:
            self.event_list_box.insert(END, event)
    
    def _get_selected_event(self):
        index = self.event_list_box.curselection()
        if len(index) > 0:
            return self._event_list[index[0]]
        else:
            return None
    
    def close(self):
        self.selected_event = self._get_selected_event()
        super().close()
        
    date = property(lambda self: self.date_entry.get())
    event_list = property(_get_event_list, _set_event_list)
