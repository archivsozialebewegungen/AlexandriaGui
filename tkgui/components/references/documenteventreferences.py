'''
Created on 03.10.2015

@author: michael
'''

from injector import inject
from tkgui import guiinjectorkeys
from tkgui.components.references.basereference import ReferencesWidgetFactory,\
    ReferenceView, Action

class DocumentEventReferencesWidgetFactory(ReferencesWidgetFactory):
    
    @inject
    def __init__(self, view_class: guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_VIEW_CLASS_KEY,
            presenter: guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_PRESENTER_KEY,
            event_selection_dialog: guiinjectorkeys.EVENT_SELECTION_DIALOG_KEY):
        print("Initalizing document event references")
        super().__init__(view_class, presenter, event_selection_dialog)
        print("Document event references initalized")
        
class DocumentEventReferencesView(ReferenceView):
    
    def __init__(self, parent, presenter, event_selection_dialog):
        print("Initializing document event references view")
        super().__init__(parent, presenter,
                _('Related events'))
        self.add_buttons()
        self.current_event = None
        self.current_document = None
        self.event_selection_dialog = event_selection_dialog
        
    def add_buttons(self):
        self.add_button(Action(_("Goto"), self.presenter.change_event))
        self.add_button(Action(_("New"), self.presenter.reference_event))
        self.add_button(Action(_("Delete"), self.presenter.remove_event_reference))

    def _get_reference_event(self):
        return self.event_selection_dialog.activate(self, default_event=self.current_event)

    reference_event = property(_get_reference_event)
