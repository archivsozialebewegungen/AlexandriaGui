'''
Created on 23.10.2015

@author: michael
'''
from tkinter import LEFT, END, Button, Frame
import Pmw
from tkinter.constants import DISABLED, NORMAL

class ReferencesWidgetFactory:
    '''
    This is a sort of hack that is due to the nature of the
    tkinter module. When instantiating a gui component it already
    needs to know its parent. So we can't let the DI container
    initalize the component but have to do it after initialization.
    The components that get the widgets injected have to do
    the initialization by calling get_view with the parent component
    as parameter.
    '''
    
    def __init__(self, view_class, presenter, *params):
        self.view_class = view_class
        self.presenter = presenter
        self.params = params
        
    def get_view(self, parent):
        view = self.view_class(parent, self.presenter, *self.params)
        view.deactivate()
        return view

class Action:
    
    def __init__(self, label, callback):
        self.label = label
        self.callback = callback

class ReferenceView(Pmw.Group):  # @UndefinedVariable

    def __init__(
            self,
            parent,
            presenter,
            label
        ):
        super().__init__(parent)
        self.parent = parent
        self.presenter = presenter
        self.presenter.view = self

        self.listbox = Pmw.ComboBox(self.interior(),  # @UndefinedVariable
                                    entryfield_entry_width=30,
                                    dropdown=1,
                                    history=0)
        
        self.listbox.pack()

        self._add_label(label)
        self.pack(side=LEFT, padx=5, pady=5)

        self.buttonframe = Frame(self.interior())
        self.buttonframe.pack()
        self.buttons = []
        self._items = []

    def _add_label(self, label):
        self.component('tag').configure(text=label)

    def _set_items(self, items):
        self.deactivate()
        self._items = []
        scrolled_list = self.listbox.component('scrolledlist')
        scrolled_list.delete(0, scrolled_list.size())
        for item in items:
            self._items.append(item)
            scrolled_list.insert(END, str(item))
        if len(items):
            self.listbox.selectitem(0)
        else:
            self.listbox.component('entryfield').delete(0, END)
        self.activate()

    def _get_selected_item(self):
        # The listbox API is completely fucked up
        current_selection = self.listbox.curselection()
        if len(current_selection) == 0:
            return None
        selected_item = int(current_selection[0])
        return self._items[selected_item]
    
    def _get_items(self):
        return self._items

    def add_button(self, action):
        self.buttons.append(Button(self.buttonframe,
               text=action.label,
               command=action.callback))
        self.buttons[-1].pack(side=LEFT, padx=5, pady=5)

    def deactivate(self):
        for button in self.buttons:
            button.configure(state=DISABLED)

    def activate(self):
        for button in self.buttons:
            button.configure(state=NORMAL)

    def show_message(self, message_text):
        dialog = Pmw.MessageDialog(  # @UndefinedVariable
                defaultbutton = 0,
                message_text = message_text)
        dialog.activate()        
        
    items = property(_get_items, _set_items)
    selected_item = property(_get_selected_item)
