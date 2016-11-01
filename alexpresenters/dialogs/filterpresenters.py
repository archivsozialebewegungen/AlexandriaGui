'''
Created on 28.12.2015

@author: michael
'''
from alexpresenters.dialogs.abstractdialogpresenter import AbstractInputDialogPresenter
from alexandriabase.domain import GenericFilter, DocumentFilter, EventFilter

class GenericFilterDialogPresenter(AbstractInputDialogPresenter):
    
    def assemble_return_value(self):
        self.view.return_value = self._new_filter_object()
        self.view.return_value.searchterms = self.view.searchterms
        
    def _new_filter_object(self):
        return GenericFilter()
    
class DocumentFilterDialogPresenter(GenericFilterDialogPresenter):
    
    def assemble_return_value(self):
        GenericFilterDialogPresenter.assemble_return_value(self)
        self.view.return_value.location = self.view.signature
        
    def _new_filter_object(self):
        return DocumentFilter()

class EventFilterDialogPresenter(GenericFilterDialogPresenter):
    
    def assemble_return_value(self):
        GenericFilterDialogPresenter.assemble_return_value(self)
        self.view.return_value.earliest_date = self.view.earliest_date
        self.view.return_value.latest_date = self.view.latest_date
        self.view.return_value.local_only = self.view.local_only
        self.view.return_value.unverified_only = self.view.unverified_only

    def _new_filter_object(self):
        return EventFilter()
