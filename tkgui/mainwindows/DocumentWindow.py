'''
Created on 02.12.2015

@author: michael
'''
from tkinter.constants import WORD, DISABLED, NORMAL
import Pmw
from injector import inject
from tkgui import guiinjectorkeys
from tkgui.mainwindows.BaseWindow import BaseWindow
from tkgui.components.alexwidgets import AlexText, AlexLabel

class DocumentWindow(BaseWindow):
    '''
    The window for manipulating documents.
    '''
    @inject(window_manager=guiinjectorkeys.WINDOW_MANAGER_KEY,
            presenter=guiinjectorkeys.DOCUMENT_WINDOW_PRESENTER_KEY,
            dialogs=guiinjectorkeys.DOCUMENT_WINDOW_DIALOGS_KEY,
            base_reference_factories=guiinjectorkeys.DOCUMENT_WINDOW_BASE_REFERENCES_KEY,
            additional_reference_factories=guiinjectorkeys.DOCUMENT_WINDOW_ADDITIONAL_REFERENCES_KEY,
            document_menu_additions=guiinjectorkeys.DOCUMENT_MENU_ADDITIONS_KEY)
    def __init__(self, window_manager, presenter, dialogs, base_reference_factories, additional_reference_factories, document_menu_additions):
        self.notebook = None
        self._description_widget = None
        self._condition_widget = None
        self._keywords_widget = None
        super().__init__(window_manager, presenter, dialogs, base_reference_factories + additional_reference_factories, document_menu_additions)
    
    def _change_widget_state(self, state):
        self._description_widget.configure(state=state)
        self._condition_widget.configure(state=state)
        self._keywords_widget.configure(state=state)
        
    def _clear_widgets(self):
        self._document_label.set(_("No document available"))
        self._description_widget.set('')
        self._condition_widget.set('')
        self._keywords_widget.set('')

    def _disable_widgets(self):
        self._change_widget_state(DISABLED)
        
    def _enable_widgets(self):
        self._change_widget_state(NORMAL)

    def _populate_entity_frame(self):
        # pylint: disable=no-member
        self._document_label = AlexLabel(self.entity_frame, text=_("No document available"))
        self._document_label.pack()
        self.notebook = Pmw.NoteBook(self.entity_frame) # @UndefinedVariable
        self.notebook.pack()
        description = self.notebook.add(_('Description'))
        self._description_widget = AlexText(description,
                                 font="Helvetica 12 bold",
                                 wrap=WORD,
                                 height=6,
                                 width=60)
        self._description_widget.pack()
        condition = self.notebook.add(_('Condition'))
        self._condition_widget = AlexText(condition,
                                 font="Helvetica 12 bold",
                                 wrap=WORD,
                                 height=6,
                                 width=60)
        self._condition_widget.pack()
        keywords = self.notebook.add(_('Keywords'))
        self._keywords_widget = AlexText(keywords,
                                 font="Helvetica 12 bold",
                                 wrap=WORD,
                                 height=6,
                                 width=60)
        self._keywords_widget.pack()
        self.notebook.setnaturalsize()

    def _view_to_entity(self):
        if self._entity == None:
            return None

        if self._description_widget.get() != self._entity.description:
            self._entity_has_changed = True
            self._entity.description = self._description_widget.get()
        if self._condition_widget.get() != self._entity.condition:
            self._entity_has_changed = True
            self._entity.condition = self._condition_widget.get()
        if self._keywords_widget.get() != self._entity.keywords:
            self._entity_has_changed = True
            self._entity.keywords = self._keywords_widget.get()
        
        return self._entity
    
    def _entity_to_view(self, entity):
        
        if self._entity != entity:
            self._entity_has_changed = False
            
        if self._entity == None:
            self._enable_widgets()

        self._entity = entity
        if entity == None:
            self._clear_widgets()
            self._disable_widgets()
            return
        
        if self._entity.id == None:
            self._document_label.set(_("New document"))
        else:
            self._document_label.set(_("Document no.{0:d} ({1!s})").format(self._entity.id, self._entity.document_type.description))
        self._description_widget.set(self._entity.description)
        self._condition_widget.set(self._entity.condition)
        self._keywords_widget.set(self._entity.keywords)
