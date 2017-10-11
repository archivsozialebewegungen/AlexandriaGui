'''
Created on 18.09.2015

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys

from tkgui.components.references.basereference import ReferencesWidgetFactory,\
    ReferenceView, Action

class EventCrossReferencesWidgetFactory(ReferencesWidgetFactory):
    
    @inject
    def __init__(self,
                 view_class: guiinjectorkeys.EVENT_CROSS_REFERENCES_VIEW_CLASS_KEY,
                 presenter: guiinjectorkeys.EVENT_CROSS_REFERENCES_PRESENTER_KEY,
                 event_selection_dialog: guiinjectorkeys.EVENT_SELECTION_DIALOG_KEY):
        print("Initialize event cross references")
        super().__init__(view_class, presenter, event_selection_dialog)
        print("Cross references initalized")
        
class EventCrossReferencesView(ReferenceView):
    
    def __init__(self, parent, presenter, event_selection_dialog):
        print("Initalizing event cross references view")
        super().__init__(parent, presenter,
                _('Crossreferences'))
        self.event_selection_dialog = event_selection_dialog
        self.add_buttons()
        self.current_event = None
        
    def add_buttons(self):
        self.add_button(Action(_("Goto"), self.presenter.goto_event))
        self.add_button(Action(_("New"), self.presenter.add_new_cross_reference))
        self.add_button(Action(_("Delete"), self.presenter.delete_cross_reference))
        
    def _select_new_cross_reference(self):
        return self.event_selection_dialog.activate(self)
                    
    new_cross_reference_event = property(_select_new_cross_reference)
