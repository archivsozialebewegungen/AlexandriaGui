'''
Created on 02.11.2015

@author: michael
'''
from tkgui.components.references.basereference import ReferencesWidgetFactory,\
    ReferenceView, Action
from injector import inject
from tkgui import guiinjectorkeys

class DocumentFileReferencesWidgetFactory(ReferencesWidgetFactory):
    '''
    classdocs
    '''
    @inject
    def __init__(self,
                 presenter: guiinjectorkeys.DOCUMENT_FILE_REFERENCES_PRESENTER_KEY,
                 view_class: guiinjectorkeys.DOCUMENT_FILE_REFERENCES_VIEW_CLASS_KEY,
                 file_selection_dialog: guiinjectorkeys.FILE_SELECTION_DIALOG_KEY,
                 viewers: guiinjectorkeys.DOCUMENT_FILE_VIEWERS_KEY):
        super().__init__(view_class, presenter, file_selection_dialog, viewers)
        
class DocumentFileReferencesView(ReferenceView):
    
    def __init__(self, parent, presenter, file_selection_dialog, viewers):
        super().__init__(parent, presenter,
                _('Document files'))
        self.current_document = None
        self.file_selection_dialog = file_selection_dialog
        self.viewers = viewers
        self.add_buttons()

    def add_buttons(self):
        self.add_button(Action(_("New"), self.presenter.add_file))
        self.add_button(Action(_("Replace"), self.presenter.replace_file))
        self.add_button(Action(_("Show"), self.presenter.show_file))
        self.add_button(Action(_("Delete"), self.presenter.remove_file))
        
    def show_file(self, file):
        file_info = self.selected_item
        if file_info.filetype in self.viewers:
            viewer = self.viewers[file_info.filetype]
        else:
            viewer = self.viewers['default']
        viewer.showFile(file, file_info)

    new_file = property(lambda self: self.file_selection_dialog.activate(self.parent))
    show_file = property(None, show_file)