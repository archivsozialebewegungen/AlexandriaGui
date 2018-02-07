'''
Created on 22.01.2018

@author: michael
'''
from injector import inject
from tkgui import _, guiinjectorkeys
from tkgui.components.alexwidgets import AlexLabel, AlexComboBox, AlexButton
from tkinter.ttk import Frame
from tkinter.constants import LEFT, RIDGE, X, DISABLED, NORMAL
from tkinter import messagebox

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

        self.labelframe = Frame(self)
        self.labelframe.pack()
        
        self.listbox = AlexComboBox(self)
        self.listbox.pack(fill=X)

        self._add_label(label)
        self.pack(side=LEFT, padx=5, pady=5)

        self.buttonframe = Frame(self)
        self.buttonframe.pack()
        self.buttons = []

    def _add_label(self, label):

        self.label = AlexLabel(self.labelframe)
        self.label.pack()
        self.label.set(label)

    def _set_items(self, items):
        self.deactivate()
        self.listbox.set_items(items)
        self.activate()

    def _get_selected_item(self):
        return self.listbox.get()

    def _get_items(self):
        return self.listbox.get_items()
    
    def add_button(self, action):
        self.buttons.append(AlexButton(self.buttonframe,
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

class EventTypeReferencesWidgetFactory(ReferencesWidgetFactory):
    '''
    Factory to generate the event document references view at runtime (because
    we need the parent for creation)
    '''
    
    @inject
    def __init__(self,
                 view_class: guiinjectorkeys.EVENT_TYPE_REFERENCES_VIEW_CLASS_KEY,
                 presenter:guiinjectorkeys.EVENT_TYPE_REFERENCES_PRESENTER_KEY,
                 event_type_selection_dialog: guiinjectorkeys.EVENT_TYPE_SELECTION_DIALOG_KEY):
        super().__init__(view_class, presenter, event_type_selection_dialog)
        
class EventTypeReferencesView(ReferenceView):
    '''
    View for managing the references between an event and its documents
    '''
    def __init__(self, parent, presenter, event_type_selection_dialog):
        super().__init__(parent, presenter,
                _('Event types'))
        self.parent = parent
        self.add_buttons()
        self.current_event = None
        self.new_event_type = None
        self.event_type_selection_dialog = event_type_selection_dialog
        
    def add_buttons(self):
        '''
        Method for configuring the buttons of the references view
        '''
        self.add_button(Action(_("New"), self._get_new_event_type))
        self.add_button(Action(_("Delete"), self.presenter.remove_event_type_reference))

    def _get_new_event_type(self):
        '''
        Dialog activation in the guise of a getter
        '''
        return self.event_type_selection_dialog.activate(self._set_new_event_type, _("Select new event type"))

    def _set_new_event_type(self, value):
        '''
        Callback for the event type selection dialog
        '''
        if value is not None:
            self.new_event_type = value
            self.presenter.add_event_type_reference()
            self.new_event_type = None