'''
Created on 05.05.2016

@author: michael
'''
from tkgui.dialogs.abstractdialog import AbstractInputDialog, InputDialogWindow
from tkgui.components.alexwidgets import AlexLabel, AlexEntry, AlexRadioGroup
from injector import inject
from tkgui import guiinjectorkeys
import Pmw

class GenericStringEditDialog(AbstractInputDialog):
    
    def __init__(self):
        pass
    
    def _init_dialog(self, 
                     master, 
                     label=_('Please edit string:'),
                     initvalue = ''):
        self.dialog = InputDialogWindow(master)
        AlexLabel(self.dialog.interior(), text=label).pack()
        self.entry = AlexEntry(self.dialog.interior())
        self.entry.set(initvalue)
        self.entry.pack()
        
    def _dialog_close(self, button):
        if button == _('Cancel'):
            self.return_value = None
        else:
            self.return_value = self.entry.get()
        self.dialog.deactivate()

class GenericStringSelectionDialog(AbstractInputDialog):
    
    def __init__(self):
        pass

    def _init_dialog(self, 
                     master, 
                     label=_('Please select:'),
                     choices = []):
        self.choices = choices
        self.dialog = InputDialogWindow(master)
        self.entry = AlexRadioGroup(self.dialog.interior(), 
                                    choices=self.choices, 
                                    title=label)
        self.entry.pack()
        
    def _dialog_close(self, button):
        if button == _('Cancel'):
            self.return_value = None
        else:
            self.return_value = self.choices[self.entry.get()]
        self.dialog.deactivate()

class GenericBooleanSelectionDialog(AbstractInputDialog):

    def __init__(self):
        pass

    def _init_dialog(self, 
                     master, 
                     question=_('Select yes or no'),
                     choices = []):
        self.choices = choices
        self.dialog = Pmw.Dialog(master,  # @UndefinedVariable
                                 buttons=(_('Yes'), _('No')),
                                 defaultbutton=_('Yes'),
                                 )
        label = AlexLabel(self.dialog.interior())
        label.set(question)
        label.pack()

    def _dialog_close(self, button):
        if button == _('Yes'):
            self.return_value = True
        else:
            self.return_value = False
        self.dialog.deactivate()
