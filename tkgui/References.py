'''
Created on 22.01.2018

@author: michael
'''
from injector import inject, InstanceProvider, ClassProvider, singleton, Module
from tkgui import _, guiinjectorkeys
from tkgui.AlexWidgets import AlexLabel, AlexComboBox, AlexButton
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
        self.labelframe.pack(pady=5)
        
        self.listbox = AlexComboBox(self)
        self.listbox.pack(fill=X, padx=5)

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

class EventCrossReferencesWidgetFactory(ReferencesWidgetFactory):
    
    @inject
    def __init__(self,
                 view_class: guiinjectorkeys.EVENT_CROSS_REFERENCES_VIEW_CLASS_KEY,
                 presenter: guiinjectorkeys.EVENT_CROSS_REFERENCES_PRESENTER_KEY,
                 event_selection_dialog: guiinjectorkeys.EVENT_SELECTION_DIALOG_KEY,
                 deletion_dialog: guiinjectorkeys.GENERIC_BOOLEAN_SELECTION_DIALOG_KEY):
        
        super().__init__(view_class, presenter, event_selection_dialog,
                         deletion_dialog)
        
class EventCrossReferencesView(ReferenceView):
    
    def __init__(self, parent, presenter,
                 event_selection_dialog,
                 deletion_dialog):
        super().__init__(parent, presenter,
                _('Crossreferences'))
        self.event_selection_dialog = event_selection_dialog
        self.add_buttons()
        self.current_event = None
        self.new_cross_reference_event = None
        self.deletion_dialog = deletion_dialog
        
    def add_buttons(self):
        self.add_button(Action(_("Goto"), self.presenter.goto_event))
        self.add_button(Action(_("New"), self._select_new_cross_reference))
        self.add_button(Action(_("Delete"), self._delete_cross_reference))
        
    def _select_new_cross_reference(self):
        
        self.event_selection_dialog.activate(self._event_selection_callback)
        
    def _event_selection_callback(self, value):
        if value is not None:
            self.new_cross_reference_event = value
            self.presenter.add_new_cross_reference()
            self.new_cross_reference_event = None

    def _delete_cross_reference(self):
        
        self.deletion_dialog.activate(self._delete_cross_reference_callback,
                                     question=_('Do you really want to\ndelete the cross reference?'))
        
    def _delete_cross_reference_callback(self, value):
        
        if value:
            self.presenter.delete_cross_reference()
            
class EventDocumentReferencesWidgetFactory(ReferencesWidgetFactory):
    '''
    Factory to generate the event document references view at runtime (because
    we need the parent for creation)
    '''
    
    @inject
    def __init__(self,
                 view_class: guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_VIEW_CLASS_KEY,
                 presenter: guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_PRESENTER_KEY,
                 documentid_selection_dialog: guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_KEY,
                 deletion_dialog: guiinjectorkeys.GENERIC_BOOLEAN_SELECTION_DIALOG_KEY):
        super().__init__(view_class, presenter, documentid_selection_dialog, deletion_dialog)
        
class EventDocumentReferencesView(ReferenceView):
    '''
    View for managing the references between an event and its documents
    '''
    def __init__(self, parent, presenter, documentid_selection_dialog,
                 deletion_dialog):
        super().__init__(parent, presenter,
                _('Related documents'))
        self.parent = parent
        self.add_buttons()
        self.current_event = None
        self.current_document = None
        self.new_document_id = None
        self.documentid_selection_dialog = documentid_selection_dialog
        self.deletion_dialog = deletion_dialog
        
    def add_buttons(self):
        '''
        Method for configuring the buttons of the references view
        '''
        self.add_button(Action(_("Goto"), self.presenter.change_document))
        self.add_button(Action(_("New"), self._get_new_document_id))
        self.add_button(Action(_("Delete"), self._remove_document_reference))

    def _get_new_document_id(self):
        '''
        Dialog activation in the guise of a getter
        '''
        return self.documentid_selection_dialog.activate(self._set_new_reference, initvalue=self.current_document.id)

    def _set_new_reference(self, value):
        '''
        Callback for the document selection dialog
        '''
        if value is not None:
            self.new_document_id = value
            self.presenter.reference_document()

    def _remove_document_reference(self):
        
        self.deletion_dialog.activate(self._remove_document_reference_callback,
                                      question=_('Do you really want to unlink\nevent from document?'))
        
    def _remove_document_reference_callback(self, value):
        
        if value:
            self.presenter.remove_document_reference()
            
class EventTypeReferencesWidgetFactory(ReferencesWidgetFactory):
    '''
    Factory to generate the event document references view at runtime (because
    we need the parent for creation)
    '''
    
    @inject
    def __init__(self,
                 view_class: guiinjectorkeys.EVENT_TYPE_REFERENCES_VIEW_CLASS_KEY,
                 presenter:guiinjectorkeys.EVENT_TYPE_REFERENCES_PRESENTER_KEY,
                 event_type_selection_dialog: guiinjectorkeys.EVENT_TYPE_SELECTION_DIALOG_KEY,
                 deletion_dialog: guiinjectorkeys.GENERIC_BOOLEAN_SELECTION_DIALOG_KEY):
        super().__init__(view_class, presenter, event_type_selection_dialog, deletion_dialog)
        
class EventTypeReferencesView(ReferenceView):
    '''
    View for managing the references between an event and its documents
    '''
    def __init__(self, parent, presenter, event_type_selection_dialog, deletion_dialog):
        super().__init__(parent, presenter,
                _('Event types'))
        self.parent = parent
        self.add_buttons()
        self.current_event = None
        self.new_event_type = None
        self.event_type_selection_dialog = event_type_selection_dialog
        self.deletion_dialog = deletion_dialog
        
    def add_buttons(self):
        '''
        Method for configuring the buttons of the references view
        '''
        self.add_button(Action(_("New"), self._get_new_event_type))
        self.add_button(Action(_("Delete"), self._remove_event_type_reference))

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

    def _remove_event_type_reference(self):
        
        self.deletion_dialog.activate(self._remove_event_type_reference_callback,
                                      question=_('Do you really want to\nremove the event type?'))
        
        
    def _remove_event_type_reference_callback(self, value):
        
        if value:
            self.presenter.remove_event_type_reference()
            
class DocumentEventReferencesWidgetFactory(ReferencesWidgetFactory):
    
    @inject
    def __init__(self,
                 view_class: guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_VIEW_CLASS_KEY,
                 presenter: guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_PRESENTER_KEY,
                 event_selection_dialog: guiinjectorkeys.EVENT_SELECTION_DIALOG_KEY,
                 deletion_dialog: guiinjectorkeys.GENERIC_BOOLEAN_SELECTION_DIALOG_KEY):
        super().__init__(view_class, presenter, event_selection_dialog, deletion_dialog)
        
class DocumentEventReferencesView(ReferenceView):
    
    def __init__(self, parent, presenter, event_selection_dialog, deletion_dialog):
        super().__init__(parent, presenter,
                _('Related events'))
        self.add_buttons()
        self.current_event = None
        self.current_document = None
        self.reference_event = None
        self.event_selection_dialog = event_selection_dialog
        self.deletion_dialog = deletion_dialog
        
    def add_buttons(self):
        self.add_button(Action(_("Goto"), self.presenter.change_event))
        self.add_button(Action(_("New"), self._get_reference_event))
        self.add_button(Action(_("Delete"), self._remove_event_reference))

    def _get_reference_event(self):
        return self.event_selection_dialog.activate(self._get_reference_event_callback, default_event=self.current_event)

    def _get_reference_event_callback(self, event):
        
        if event is None:
            return
        self.reference_event = event
        self.presenter.reference_event()
        self.reference_event = None

    def _remove_event_reference(self):
        
        self.deletion_dialog.activate(self._remove_event_reference_callback,
                                      question=_('Do you really want to\nunlink event from document?'))
        
    def _remove_event_reference_callback(self, value):
        
        if value:
            self.presenter.remove_event_reference()
            
class DocumentFileReferencesWidgetFactory(ReferencesWidgetFactory):
    '''
    classdocs
    '''
    @inject
    def __init__(self,
                 presenter: guiinjectorkeys.DOCUMENT_FILE_REFERENCES_PRESENTER_KEY,
                 view_class: guiinjectorkeys.DOCUMENT_FILE_REFERENCES_VIEW_CLASS_KEY,
                 file_selection_dialog: guiinjectorkeys.FILE_SELECTION_DIALOG_KEY,
                 deletion_dialog: guiinjectorkeys.GENERIC_BOOLEAN_SELECTION_DIALOG_KEY,
                 viewers: guiinjectorkeys.DOCUMENT_FILE_VIEWERS_KEY):
        super().__init__(view_class, presenter, file_selection_dialog, deletion_dialog, viewers)
        
class DocumentFileReferencesView(ReferenceView):
    
    def __init__(self, parent, presenter, file_selection_dialog, deletion_dialog, viewers):
        super().__init__(parent, presenter,
                _('Document files'))
        self.current_document = None
        self.file_selection_dialog = file_selection_dialog
        self.deletion_dialog = deletion_dialog
        self.viewers = viewers
        self.add_buttons()

    def add_buttons(self):
        self.add_button(Action(_("New"), self._add_file))
        self.add_button(Action(_("Replace"), self._replace_file))
        self.add_button(Action(_("Show"), self.presenter.show_file))
        self.add_button(Action(_("Delete"), self._remove_file))
    
    def _add_file(self):
        
        self.file_selection_dialog.activate(self._add_file_callback)
        
    def _add_file_callback(self, file):
        
        if file is None:
            return
        self.new_file = file
        self.presenter.add_file()
        self.new_file = None
        
    def _replace_file(self):
        
        self.file_selection_dialog.activate(self._replace_file_callback)
        
    def _replace_file_callback(self, file):
        
        if file is None:
            return
        self.new_file = file
        self.presenter.replace_file()
        self.new_file = None
        
    def _remove_file(self):
        
        self.deletion_dialog.activate(self._remove_file_callback,
                                      question=_('Do you really want to remove\nthe file from the document?'))
        
    def _remove_file_callback(self, value):
        
        if value:
            self.presenter.remove_file()

    def show_file(self, file):
        file_info = self.selected_item
        viewer = self.viewers[file_info.filetype]
        viewer.showFile(file, file_info)

    show_file = property(None, show_file)
    
class WindowReferencesModule(Module):
    
    def configure(self, binder):
        
        binder.bind(guiinjectorkeys.EVENT_CROSS_REFERENCES_FACTORY_KEY,
                    ClassProvider(EventCrossReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_FACTORY_KEY,
                    ClassProvider(DocumentEventReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_FACTORY_KEY,
                    ClassProvider(EventDocumentReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_FACTORY_KEY,
                    ClassProvider(DocumentFileReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_REFERENCES_FACTORY_KEY,
                    ClassProvider(EventTypeReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_CROSS_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(EventCrossReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(DocumentFileReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(DocumentEventReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(EventDocumentReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(EventTypeReferencesView), scope=singleton)
