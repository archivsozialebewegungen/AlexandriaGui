'''
Created on 23.10.2015

@author: michael
'''
from tkinter import StringVar, messagebox
from tkinter.ttk import Button, Frame, Combobox
from tkinter.constants import X, LEFT, DISABLED, NORMAL, RIDGE
from tkgui.components.alexwidgets import AlexLabel

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

class ReferenceView(Frame):  # @UndefinedVariable

    def __init__(
            self,
            parent,
            presenter,
            label
        ):
        super().__init__(parent, borderwidth=1, relief=RIDGE)
        self.parent = parent
        self.presenter = presenter
        self.presenter.view = self

        self._selection = StringVar()
        
        self.labelframe = Frame(self)
        self.labelframe.pack()
        
        self.listbox = Combobox(self,  
                                state='readonly',
                                textvariable=self._selection)
        
        self.listbox.pack(fill=X)

        self._add_label(label)
        self.pack(side=LEFT, padx=5, pady=5)

        self.buttonframe = Frame(self)
        self.buttonframe.pack()
        self.buttons = []
        self._items = {}

    def _add_label(self, label):

        self.label = AlexLabel(self.labelframe)
        self.label.pack()
        self.label.set(label)

    def _set_items(self, items):
        self.deactivate()
        self._items = {}
        values = []
        
        for item in items:
            self._items["%s" % item] = (item)
            values.append("%s" % item)

        self.listbox.configure(values=values)
            
        if len(items):
            self._selection.set("%s" % items[0])
        self.activate()

    def _get_selected_item(self):
        if self._selection.get() in self.items:
            return self.items[self._selection.get()]
        else:
            return None
    
    def _get_items(self):
        return list(self._items.values())

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
        messagebox.showinfo(_("Hint"), message_text)
        
    items = property(_get_items, _set_items)
    selected_item = property(_get_selected_item)
