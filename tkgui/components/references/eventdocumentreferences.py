'''
Created on 03.10.2015

@author: michael
'''

from injector import inject
from tkgui import guiinjectorkeys
from tkgui.components.references.basereference import ReferencesWidgetFactory,\
    ReferenceView, Action

class EventDocumentReferencesWidgetFactory(ReferencesWidgetFactory):
    '''
    Factory to generate the event document references view at runtime (because
    we need the parent for creation)
    '''
    
    @inject
    def __init__(self,
                 view_class: guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_VIEW_CLASS_KEY,
                 presenter: guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_PRESENTER_KEY,
                 documentid_selection_dialog: guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_KEY):
        print("Initializing event document references")
        super().__init__(view_class, presenter, documentid_selection_dialog)
        print("Document event references initialized")
        
class EventDocumentReferencesView(ReferenceView):
    '''
    View for managing the references between an event and its documents
    '''
    def __init__(self, parent, presenter, documentid_selection_dialog):
        print("Initializing event document references view")
        super().__init__(parent, presenter,
                _('Related documents'))
        self.parent = parent
        self.add_buttons()
        self.current_event = None
        self.current_document = None
        self.documentid_selection_dialog = documentid_selection_dialog
        
    def add_buttons(self):
        '''
        Method for configuring the buttons of the references view
        '''
        self.add_button(Action(_("Goto"), self.presenter.change_document))
        self.add_button(Action(_("New"), self.presenter.reference_document))
        self.add_button(Action(_("Delete"), self.presenter.remove_document_reference))

    def _get_new_documentid(self):
        '''
        Dialog activation in the guise of a getter
        '''
        return self.documentid_selection_dialog.activate(self.parent, self.current_document.id)

    new_documentid = property(_get_new_documentid)
