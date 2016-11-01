'''
Created on 27.12.2015

@author: michael
'''
import Pmw
from tkinter.constants import W
from tkgui.dialogs.abstractdialog import AbstractInputDialog
from tkgui.components.alexwidgets import AlexLabel, AlexEntry, AlexCheckBox
from tkgui.components.alexwidgets import AlexDateEntry

from tkgui import guiinjectorkeys
from injector import inject

class GenericFilterDialog(AbstractInputDialog):
    
    def _init_dialog(self, master):
        # We want to reuse the filter dialog if it already exists
        if self.dialog != None:
            return
        # pylint: disable=no-member
        self.dialog = Pmw.Dialog(buttons=(_("Set filter"), _("Clear form"), _("Cancel")))  # @UndefinedVariable
        self.search_term_entries = []
        for i in range(1, 4):
            AlexLabel(self.dialog.interior(),
                      text=_("%d. search expression:" % i)).grid(row=i - 1, column=0, sticky=W)
            entry = AlexEntry(self.dialog.interior())
            entry.grid(row=i - 1, column=1, sticky=W, pady=5)
            self.search_term_entries.append(entry)

    def _dialog_close(self, button):
        if button == _('Clear form'):
            self._clear_filter_form()
            return
        if button == _('Set filter'):
            self.presenter.assemble_return_value()
        self.dialog.deactivate()

    def _clear_filter_form(self):
        for entry in self.search_term_entries:
            entry.set('')

    def _get_searchterms(self):
        searchterms = []
        for entry in self.search_term_entries:
            value = entry.get()
            if value != '':
                searchterms.append(value)
        return searchterms
    
    searchterms = property(_get_searchterms)

class DocumentFilterDialog(GenericFilterDialog):  # @UndefinedVariable

    @inject(presenter=guiinjectorkeys.DOCUMENT_FILTER_DIALOG_PRESENTER_KEY)    
    def __init__(self, presenter):
        super().__init__(presenter)

    def _init_dialog(self, master):
        self.master = master
        if self.dialog != None:
            return
        super()._init_dialog(master)
        AlexLabel(self.dialog.interior(), text=_("Signature:")).grid(row=3, column=0, sticky=W)
        self.signature_entry = AlexEntry(self.dialog.interior())
        self.signature_entry.grid(row=3, column=1, sticky=W, pady=5)
                   
    def _clear_filter_form(self):
        super()._clear_filter_form()
        self.signature_entry.set('')
    
    signature = property(lambda self: self.signature_entry.get())
    
class EventFilterDialog(GenericFilterDialog):

    @inject(presenter=guiinjectorkeys.EVENT_FILTER_DIALOG_PRESENTER_KEY)
    def __init__(self, presenter):
        super().__init__(presenter)

    def _init_dialog(self, master):
        if self.dialog != None:
            return
        super()._init_dialog(master)

        self.earliest_date_entry = AlexDateEntry(self.dialog.interior(), label=_("Earliest Date"))
        self.earliest_date_entry.grid(row=3, column=0, sticky=W, pady=5, columnspan=2)
        self.latest_date_entry = AlexDateEntry(self.dialog.interior(), label=_("Latest Date"))
        self.latest_date_entry.grid(row=4, column=0, sticky=W, pady=5, columnspan=2)

        AlexLabel(self.dialog.interior(), text=_("Only local events")
              ).grid(row=5, column=0, sticky=W, pady=5)
        self.local_only_checkbox = AlexCheckBox(self.dialog.interior())
        self.local_only_checkbox.grid(row=5, column=1, sticky=W, pady=5)

        AlexLabel(self.dialog.interior(), text=_("Only unverified events")
              ).grid(row=6, column=0, sticky=W, pady=5)
        self.unverified_only_checkbox = AlexCheckBox(self.dialog.interior())
        self.unverified_only_checkbox.grid(row=6, column=1, sticky=W, pady=5)
    
    def _clear_filter_form(self):
        super()._clear_filter_form()
        self.earliest_date_entry.set(None)
        self.latest_date_entry.set(None)
        self.local_only_checkbox.set(False)
        self.unverified_only_checkbox.set(False)

    earliest_date = property(lambda self: self.earliest_date_entry.get(),
                             lambda self, value: self.earliest_date_entry.set(value))
    latest_date = property(lambda self: self.latest_date_entry.get(),
                             lambda self, value: self.latest_date_entry.set(value))
    local_only = property(lambda self: self.local_only_checkbox.get(),
                             lambda self, value: self.local_only_checkbox.set(value))
    unverified_only = property(lambda self: self.unverified_only_checkbox.get(),
                             lambda self, value: self.unverified_only_checkbox.set(value))
