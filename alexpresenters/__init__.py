from injector import Module, singleton, provider,\
    ClassProvider, inject
from tkgui import guiinjectorkeys
from alexpresenters.mainwindows.EventWindowPresenter import EventWindowPresenter
from alexpresenters.components.references.eventcrossreferencespresenter import EventCrossReferencesPresenter
from alexpresenters.mainwindows.DocumentWindowPresenter import DocumentWindowPresenter
from alexpresenters.messagebroker import MessageBroker
from alexpresenters.components.references.documenteventreferencespresenter import DocumentEventReferencesPresenter
from alexpresenters.components.references.documentfilereferencespresenter import DocumentFileReferencesPresenter
from alexpresenters.components.references.eventdocumentreferencespresenter import EventDocumentReferencesPresenter
from alexpresenters.mainwindows.PostProcessors import DocumentTypePostProcessor,\
    JournalDocTypePostProcessor
from alexpresenters.components.references.event_type_references_presenter import EventTypeReferencesPresenter
from alexpresenters.DialogPresenters import AbstractInputDialogPresenter,\
    EventSelectionPresenter, DateSelectionDialogPresenter,\
    EventIdSelectionDialogPresenter, DateRangeSelectionDialogPresenter,\
    DocumentIdSelectionDialogPresenter, YearSelectionDialogPresenter,\
    EventTypeSelectionPresenter, DocumentFilterDialogPresenter,\
    EventFilterDialogPresenter, LoginDialogPresenter,\
    GenericInputDialogPresenter

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
        binder.bind(guiinjectorkeys.GENERIC_INPUT_DIALOG_PRESENTER,
                    ClassProvider(GenericInputDialogPresenter))
        binder.bind(guiinjectorkeys.DATE_SELECTION_DIALOG_PRESENTER_KEY,
                    ClassProvider(DateSelectionDialogPresenter))
        binder.bind(guiinjectorkeys.EVENT_ID_SELECTION_DIALOG_PRESENTER_KEY,
                    ClassProvider(EventIdSelectionDialogPresenter))
        binder.bind(guiinjectorkeys.EVENT_CONFIRMATION_PRESENTER_KEY,
                    ClassProvider(AbstractInputDialogPresenter))
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
        binder.bind(guiinjectorkeys.EVENT_TYPE_SELECTION_PRESENTER_KEY,
                    ClassProvider(EventTypeSelectionPresenter), scope=singleton)

        # Postprocessors
        binder.bind(guiinjectorkeys.DOCUMENT_TYPE_POST_PROCESSOR_KEY,
                    ClassProvider(DocumentTypePostProcessor), scope=singleton)
        binder.bind(guiinjectorkeys.JOURNAL_DOCUMENT_TYPE_POST_PROCESSOR_KEY,
                    ClassProvider(JournalDocTypePostProcessor), scope=singleton)
        
    @provider
    @singleton
    @inject
    def document_window_post_processors(self,
                                        document_type_post_processor: guiinjectorkeys.DOCUMENT_TYPE_POST_PROCESSOR_KEY,
                                        journal_document_type_post_processor: guiinjectorkeys.JOURNAL_DOCUMENT_TYPE_POST_PROCESSOR_KEY) -> guiinjectorkeys.DOCUMENT_WINDOW_POST_PROCESSORS_KEY:
        return (document_type_post_processor,
                journal_document_type_post_processor)
    
    @provider
    @singleton
    def event_window_post_processors(self) -> guiinjectorkeys.EVENT_WINDOW_POST_PROCESSORS_KEY:
        return ()
