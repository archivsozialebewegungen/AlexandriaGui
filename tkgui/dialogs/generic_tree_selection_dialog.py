'''
Created on 23.10.2015

@author: michael
'''
import Pmw
from tkgui.dialogs.abstractdialog import AbstractInputDialog
from tkgui.components.alexwidgets import AlexTree, AlexEntry
from tkinter.constants import X

class GenericTreeSelectionDialog(AbstractInputDialog):
    
    def __init__(self, presenter):
        
        self.presenter = presenter
        self.presenter.view = self
        self.return_value = None
        self.dialog = None
        
        self.tree_widget = None
        self.filter_is_set = False
        
    def _init_dialog(self, master, label=_('Select a tree node')):

        if self.dialog is not None:
            return
        self.label = label
        self.dialog = Pmw.Dialog(master,  # @UndefinedVariable
            buttons=(_('Select'), _('Cancel')),
            defaultbutton=_('Select'),
            title=label)
        self.dialog.withdraw()
        
        self.filter_entry = AlexEntry(self.dialog.interior())
        self.filter_entry.bind("<KeyRelease>", lambda event: self.apply_filter(event))
        self.filter_entry.pack(fill=X, expand=1)

        self.presenter.get_tree()
        
    def apply_filter(self, event):
        filter_string = self.filter_entry.get()
        if len(filter_string) > 2:
            visible_nodes = self.tree_widget.apply_filter(filter_string)
            if visible_nodes < 20:
                self.tree_widget.expand_all()
            self.filter_is_set = True
        else:
            if self.filter_is_set:
                self.tree_widget.clear_filter()
                self.filter_is_set = False
    
    def set_tree(self, tree):
        if self.dialog is None:
            return
        if self.tree_widget is not None:
            self.tree_widget.destroy()
        self.tree_widget = AlexTree(self.dialog.interior(),
                                    tree,
                                    label_text=self.label)
        self.tree_widget.pack()
            
    input = property(lambda self: self.tree_widget.get())
    tree = property(None, set_tree)
