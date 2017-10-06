'''
Created on 23.10.2015

@author: michael
'''
from injector import inject
from tkgui import guiinjectorkeys
from tkgui.dialogs.generic_tree_selection_dialog import GenericTreeSelectionDialog

class EventTypeSelectionDialog(GenericTreeSelectionDialog):
    
    @inject
    def __init__(self, presenter: guiinjectorkeys.EVENT_TYPE_SELECTION_PRESENTER_KEY):
        super().__init__(presenter)
