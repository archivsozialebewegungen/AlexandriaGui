from injector import Module, ClassProvider, singleton, provides, inject
from tkgui import guiinjectorkeys
from alexpresenters.components.references.eventcrossreferencespresenter import EventCrossReferencesPresenter
from tkgui.components.references.eventcrossreferences import EventCrossReferencesWidgetFactory,\
    EventCrossReferencesView
from tkgui.components.references.documentfilereference import DocumentFileReferencesView,\
    DocumentFileReferencesWidgetFactory
from tkgui.components.references.documenteventreferences import DocumentEventReferencesWidgetFactory,\
    DocumentEventReferencesView
from tkgui.components.references.eventdocumentreferences import EventDocumentReferencesView,\
    EventDocumentReferencesWidgetFactory
from tkgui.components.references.event_type_references import EventTypeReferencesWidgetFactory,\
    EventTypeReferencesView

class WindowReferencesModule(Module):
    
    def configure(self, binder):
        
        # Factories
        binder.bind(guiinjectorkeys.EVENT_CROSS_REFERENCES_FACTORY_KEY, ClassProvider(EventCrossReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_FACTORY_KEY, ClassProvider(DocumentEventReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_FACTORY_KEY, ClassProvider(EventDocumentReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_FACTORY_KEY, ClassProvider(DocumentFileReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_REFERENCES_FACTORY_KEY, ClassProvider(EventTypeReferencesWidgetFactory), scope=singleton)


    @provides(guiinjectorkeys.EVENT_CROSS_REFERENCES_VIEW_CLASS_KEY, scope=singleton)
    def event_crossreferences_view_class(self):
        return EventCrossReferencesView

    @provides(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_VIEW_CLASS_KEY, scope=singleton)
    def document_file_references_view_class(self):
        return DocumentFileReferencesView

    @provides(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_VIEW_CLASS_KEY, scope=singleton)
    def document_event_references_view_class(self):
        return DocumentEventReferencesView

    @provides(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_VIEW_CLASS_KEY, scope=singleton)
    def event_document_references_view_class(self):
        return EventDocumentReferencesView

    @provides(guiinjectorkeys.EVENT_TYPE_REFERENCES_VIEW_CLASS_KEY, scope=singleton)
    def event_type_references_view_class(self):
        return EventTypeReferencesView
