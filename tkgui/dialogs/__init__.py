'''
Module configuration for dialogs
'''
from injector import Module, singleton, provider, \
    ClassProvider
from tkgui import guiinjectorkeys
from tkgui.dialogs.eventselectiondialog import EventSelectionDialog
from tkgui.dialogs.dateselectiondialog import DateSelectionDialog, \
    DateRangeSelectionDialog, SimpleDateSelectionDialog
from alexpresenters.dialogs.dateselectiondialogpresenter import DateSelectionDialogPresenter
from alexpresenters.dialogs.yearselectiondialogpresenter import YearSelectionDialogPresenter
from tkgui.dialogs.filterdialogs import DocumentFilterDialog, EventFilterDialog
from alexpresenters.dialogs.filterpresenters import DocumentFilterDialogPresenter,\
    EventFilterDialogPresenter
from alexpresenters.dialogs.documentid_selection_dialog_presenter import \
    DocumentIdSelectionDialogPresenter
from tkgui.dialogs.documentidselectiondialog import DocumentIdSelectionDialog
from tkgui.dialogs.fileselectiondialog import FileSelectionDialog
from alexpresenters.dialogs.logindialogpresenter import LoginDialogPresenter
from tkgui.dialogs.logindialog import LoginDialog
from tkgui.dialogs.GenericInputDialogs import GenericStringEditDialog,\
    GenericStringSelectionDialog
from alexpresenters.dialogs.eventtypeselectionpresenter import EventTypeSelectionPresenter
from tkgui.dialogs.event_type_selection_dialog import EventTypeSelectionDialog
from tkgui.dialogs.event_confirmation_dialog import EventConfirmationDialog
from alexpresenters.dialogs.daterangeselectiondialogpresenter \
    import DateRangeSelectionDialogPresenter
from tkgui.dialogs.yearselectiondialog import YearSelectionDialog
from alexpresenters.dialogs.eventselectionpresenter import EventSelectionPresenter

class DialogsTkGuiModule(Module):
    '''
    Binds all existing dialogs.
    '''
    def configure(self, binder):
        binder.bind(guiinjectorkeys.EVENT_CONFIRMATION_DIALOG_KEY,
                    ClassProvider(EventConfirmationDialog))
        binder.bind(guiinjectorkeys.GENERIC_STRING_EDIT_DIALOG_KEY,
                    ClassProvider(GenericStringEditDialog))
        binder.bind(guiinjectorkeys.GENERIC_STRING_SELECTION_DIALOG_KEY,
                    ClassProvider(GenericStringSelectionDialog))
        binder.bind(guiinjectorkeys.DATE_SELECTION_DIALOG_KEY,
                    ClassProvider(SimpleDateSelectionDialog))
        binder.bind(guiinjectorkeys.DATERANGE_SELECTION_DIALOG_KEY,
                    ClassProvider(DateRangeSelectionDialog))
        binder.bind(guiinjectorkeys.YEAR_SELECTION_DIALOG_KEY,
                    ClassProvider(YearSelectionDialog))
        binder.bind(guiinjectorkeys.EVENT_SELECTION_DIALOG_KEY,
                    ClassProvider(EventSelectionDialog))
        binder.bind(guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_KEY,
                    ClassProvider(DocumentIdSelectionDialog))
        binder.bind(guiinjectorkeys.DOCUMENT_FILTER_DIALOG_KEY,
                    ClassProvider(DocumentFilterDialog), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_FILTER_DIALOG_KEY,
                    ClassProvider(EventFilterDialog), scope=singleton)
        binder.bind(guiinjectorkeys.LOGIN_DIALOG_KEY,
                    ClassProvider(LoginDialog), scope=singleton)
        binder.bind(guiinjectorkeys.FILE_SELECTION_DIALOG_KEY,
                    ClassProvider(FileSelectionDialog), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_SELECTION_DIALOG_KEY,
                    ClassProvider(EventTypeSelectionDialog), scope=singleton)
