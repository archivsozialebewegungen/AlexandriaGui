'''
Created on 03.10.2015

@author: michael
'''

from injector import inject
from tkgui import guiinjectorkeys
from tkgui.components.references.basereference import ReferencesWidgetFactory,\
    ReferenceView, Action

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
        self.event_type_selection_dialog = event_type_selection_dialog
        
    def add_buttons(self):
        '''
        Method for configuring the buttons of the references view
        '''
        self.add_button(Action(_("New"), self.presenter.add_event_type_reference))
        self.add_button(Action(_("Delete"), self.presenter.remove_event_type_reference))

    def _get_new_event_type(self):
        '''
        Dialog activation in the guise of a getter
        '''
        return self.event_type_selection_dialog.activate(self.parent, _("Select new event type"))

    new_event_type = property(_get_new_event_type)
