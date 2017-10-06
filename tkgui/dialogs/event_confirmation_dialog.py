'''
Created on 23.10.2015

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys
from tkgui.dialogs.generic_tree_selection_dialog import GenericTreeSelectionDialog
import Pmw
from tkinter import Frame, Label, Button
from tkinter.constants import LEFT, W

class EventConfirmationDialog(GenericTreeSelectionDialog):
    
    @inject
    def __init__(self, presenter: guiinjectorkeys.EVENT_CONFIRMATION_PRESENTER_KEY):
        super().__init__(presenter)
        self.date = None
        self.event_list = []
        
    def _init_dialog(self, master, date):
        self.date = date
        self.presenter.set_event_list()
        if len(self.event_list) == 0:
            self.dialog = None
            return
        
        self.dialog = Pmw.Dialog(master,  # @UndefinedVariable
            buttons = (_('Create new event'),),
            defaultbutton = _('Create new event'),
            title = _('Confirm event creation'),
            command =lambda button: self._dialog_close(None))
        self.dialog.withdraw()
        Label(self.dialog.interior(),
              text=_("Events exist on %s. Please select the event you want or create a new one") % date,
              wraplength=550,
              font=("Helvetica", 14, "bold")).pack() 
        event_frame = Frame(self.dialog.interior())
        event_frame.pack()
        row_counter = 0
        for event in self.event_list:
            description = Label(event_frame, wraplength=500, justify=LEFT, text=event.description)
            description.grid(row=row_counter, column=0, sticky=W)
            def closure(event):
                return lambda: self._dialog_close(event)
            button = Button(event_frame, text=_("Goto event"),
                            command=closure(event))
            button.grid(row=row_counter, column=1)
            row_counter += 1

    def activate(self, master=None, *params, **kw):
        self._init_dialog(master, *params, **kw)
        if self.dialog is None:
            return None
        self.dialog.activate()
        return self.return_value
            
    def _dialog_close(self, event):
        if event is None:
            self.return_value = None
        else:
            self.return_value = event
        self.dialog.deactivate()

