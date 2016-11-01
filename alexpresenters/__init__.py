from injector import Module, singleton, provides,\
    ClassProvider, inject
from tkgui import guiinjectorkeys
from alexpresenters.dialogs.eventselectionpresenter import EventSelectionPresenter
from alexpresenters.mainwindows.EventWindowPresenter import EventWindowPresenter
from alexpresenters.components.references.eventcrossreferencespresenter import EventCrossReferencesPresenter
from alexpresenters.mainwindows.DocumentWindowPresenter import DocumentWindowPresenter
from alexpresenters.dialogs.dateselectiondialogpresenter import DateSelectionDialogPresenter
from alexpresenters.messagebroker import MessageBroker
from alexpresenters.components.references.documenteventreferencespresenter import DocumentEventReferencesPresenter
from alexpresenters.components.references.documentfilereferencespresenter import DocumentFileReferencesPresenter
from alexpresenters.components.references.eventdocumentreferencespresenter import EventDocumentReferencesPresenter
from alexpresenters.dialogs.logindialogpresenter import LoginDialogPresenter
from alexpresenters.mainwindows.PostProcessors import DocumentTypePostProcessor,\
    JournalDocTypePostProcessor
from alexpresenters.dialogs.daterangeselectiondialogpresenter import DateRangeSelectionDialogPresenter
from alexpresenters.dialogs.yearselectiondialogpresenter import YearSelectionDialogPresenter
from alexpresenters.dialogs.documentid_selection_dialog_presenter import DocumentIdSelectionDialogPresenter
from alexpresenters.dialogs.filterpresenters import DocumentFilterDialogPresenter,\
    EventFilterDialogPresenter
from alexpresenters.components.references.event_type_references_presenter import EventTypeReferencesPresenter
from alexpresenters.dialogs.eventconfirmationpresenter import EventConfirmationPresenter

class PresentersModule(Module):
    
    def configure(self, binder):
        # General
        binder.bind(guiinjectorkeys.MESSAGE_BROKER_KEY,
                    ClassProvider(MessageBroker), scope=singleton)
        # References
        binder.bind(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_PRESENTER_KEY,
                    ClassProvider(DocumentEventReferencesPresenter), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_PRESENTER_KEY,
                    ClassProvider(EventDocumentReferencesPresenter), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_CROSS_REFERENCES_PRESENTER_KEY,
                    ClassProvider(EventCrossReferencesPresenter), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_PRESENTER_KEY,
                    ClassProvider(DocumentFileReferencesPresenter), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_REFERENCES_PRESENTER_KEY,
                    ClassProvider(EventTypeReferencesPresenter), scope=singleton)
        # MainWindows
        binder.bind(guiinjectorkeys.EVENT_WINDOW_PRESENTER_KEY,
                    ClassProvider(EventWindowPresenter), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_WINDOW_PRESENTER_KEY,
                    ClassProvider(DocumentWindowPresenter), scope=singleton)
        # Dialogs
        binder.bind(guiinjectorkeys.DATE_SELECTION_DIALOG_PRESENTER_KEY,
                    ClassProvider(DateSelectionDialogPresenter))
        binder.bind(guiinjectorkeys.EVENT_CONFIRMATION_PRESENTER_KEY,
                    ClassProvider(EventConfirmationPresenter))
        binder.bind(guiinjectorkeys.DATERANGE_SELECTION_DIALOG_PRESENTER_KEY,
                    ClassProvider(DateRangeSelectionDialogPresenter))
        binder.bind(guiinjectorkeys.YEAR_SELECTION_DIALOG_PRESENTER_KEY,
                    ClassProvider(YearSelectionDialogPresenter))
        binder.bind(guiinjectorkeys.EVENT_SELECTION_DIALOG_PRESENTER_KEY,
                    ClassProvider(EventSelectionPresenter))
        binder.bind(guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_PRESENTER_KEY,
                    ClassProvider(DocumentIdSelectionDialogPresenter))
        binder.bind(guiinjectorkeys.DOCUMENT_FILTER_DIALOG_PRESENTER_KEY,
                    ClassProvider(DocumentFilterDialogPresenter), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_FILTER_DIALOG_PRESENTER_KEY,
                    ClassProvider(EventFilterDialogPresenter), scope=singleton)
        binder.bind(guiinjectorkeys.LOGIN_DIALOG_PRESENTER_KEY,
                    ClassProvider(LoginDialogPresenter), scope=singleton)
        # Postprocessors
        binder.bind(guiinjectorkeys.DOCUMENT_TYPE_POST_PROCESSOR_KEY,
                    ClassProvider(DocumentTypePostProcessor), scope=singleton)
        binder.bind(guiinjectorkeys.JOURNAL_DOCUMENT_TYPE_POST_PROCESSOR_KEY,
                    ClassProvider(JournalDocTypePostProcessor), scope=singleton)
        
    @provides(guiinjectorkeys.DOCUMENT_WINDOW_POST_PROCESSORS_KEY, scope=singleton)
    @inject(document_type_post_processor=guiinjectorkeys.DOCUMENT_TYPE_POST_PROCESSOR_KEY,
            journal_document_type_post_processor=guiinjectorkeys.JOURNAL_DOCUMENT_TYPE_POST_PROCESSOR_KEY)
    def document_window_post_processors(self, document_type_post_processor,
                                        journal_document_type_post_processor):
        return (document_type_post_processor,
                journal_document_type_post_processor)
    
    @provides(guiinjectorkeys.EVENT_WINDOW_POST_PROCESSORS_KEY, scope=singleton)
    def event_window_post_processors(self):
        return ()
