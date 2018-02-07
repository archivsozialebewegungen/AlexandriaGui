'''
Created on 03.10.2015

@author: michael
'''

from injector import inject
from tkgui import _, guiinjectorkeys
from tkgui.References import ReferencesWidgetFactory, ReferenceView, Action

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
        super().__init__(view_class, presenter, documentid_selection_dialog)
        
class EventDocumentReferencesView(ReferenceView):
    '''
    View for managing the references between an event and its documents
    '''
    def __init__(self, parent, presenter, documentid_selection_dialog):
        super().__init__(parent, presenter,
                _('Related documents'))
        self.parent = parent
        self.add_buttons()
        self.current_event = None
        self.current_document = None
        self.new_document_id = None
        self.documentid_selection_dialog = documentid_selection_dialog
        
    def add_buttons(self):
        '''
        Method for configuring the buttons of the references view
        '''
        self.add_button(Action(_("Goto"), self.presenter.change_document))
        self.add_button(Action(_("New"), self._get_new_document_id))
        self.add_button(Action(_("Delete"), self.presenter.remove_document_reference))

    def _get_new_document_id(self):
        '''
        Dialog activation in the guise of a getter
        '''
        return self.documentid_selection_dialog.activate(self._set_new_reference, self.current_document.id)

    def _set_new_reference(self, value):
        '''
        Callback for the document selection dialog
        '''
        if value is not None:
            self.new_document_id = value
            self.presenter.reference_document()
