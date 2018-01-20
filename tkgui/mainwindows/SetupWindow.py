'''
Created on 25.10.2017

@author: michael
'''
from tkinter.ttk import Frame, Button
from injector import inject
from tkgui.components.alexwidgets import AlexComboBox
from tkinter.constants import LEFT
from tkgui import guiinjectorkeys

class LoginDialog(Frame):
    '''
    Window used during setup for the user login
    '''

    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.LOGIN_DIALOG_PRESENTER_KEY):
        
        self.window_manager = window_manager
        self.window = None
        self.presenter = presenter
        self.presenter.view = self
        
    def create_dialog(self):
        
        self.window = self.window_manager.create_new_window()
        self.window.withdraw()
        
        super().__init__(self.window)
        self.pack()
        
        self.combobox = AlexComboBox(self)
        self.combobox.pack()
        
        buttonframe = Frame(self)
        buttonframe.pack()
        
        Button(buttonframe, text=_('OK'), command=self.presenter.ok_action).pack(side=LEFT)
        Button(buttonframe, text=_('Cancel'), command=self.presenter.cancel_action).pack(side=LEFT)
        
        self._return_value = None

    def activate(self):
        self.create_dialog()
        self.presenter.init_view_action()
        self.window.wait_window()
        return self._return_value

    def _set_return_value(self, value):
        self._return_value = value
        self.window_manager.remove_window(self.window)
        self.window = None
        
    def _set_creators(self, creators):
        self.combobox.set_items(creators)
        
    def _get_selected_creator(self):
        return self.combobox.get()
    
    return_value = property(None, _set_return_value)
    creators = property(None, _set_creators)
    selected_creator = property(_get_selected_creator)