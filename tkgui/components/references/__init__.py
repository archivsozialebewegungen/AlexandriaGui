from injector import Module, ClassProvider, singleton, provides, inject,\
    InstanceProvider
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
        
        binder.bind(guiinjectorkeys.EVENT_CROSS_REFERENCES_FACTORY_KEY,
                    ClassProvider(EventCrossReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_FACTORY_KEY,
                    ClassProvider(DocumentEventReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_FACTORY_KEY,
                    ClassProvider(EventDocumentReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_FACTORY_KEY,
                    ClassProvider(DocumentFileReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_REFERENCES_FACTORY_KEY,
                    ClassProvider(EventTypeReferencesWidgetFactory), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_CROSS_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(EventCrossReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_FILE_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(DocumentFileReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(DocumentEventReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(EventDocumentReferencesView), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_REFERENCES_VIEW_CLASS_KEY,
                    InstanceProvider(EventTypeReferencesView), scope=singleton)
