'''
Window module
'''
from injector import Module, ClassProvider, singleton, provider, inject,\
    InstanceProvider
from alexandriabase import baseinjectorkeys
from tkgui import guiinjectorkeys
from tkgui.mainwindows.EventWindow import EventWindow
from tkgui.mainwindows.DocumentWindow import DocumentWindow
from tkgui.mainwindows.BaseWindow import WindowManager, BaseWindow
from tkgui.mainwindows import fileviewers
from tkgui.mainwindows.fileviewers import ExternalViewer
# pylint: disable=no-self-use

class MainWindowsModule(Module):
    '''
    Rather complicated injector module that constructs the main
    windows of the application with dialogs and reference widgets.
    '''
    
    def configure(self, binder):
      
        binder.bind(guiinjectorkeys.WINDOW_MANAGER_KEY,
                    ClassProvider(WindowManager), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_WINDOW_KEY,
                    ClassProvider(EventWindow), scope=singleton)
        binder.bind(guiinjectorkeys.DOCUMENT_WINDOW_KEY,
                    ClassProvider(DocumentWindow), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_MENU_ADDITIONS_KEY,
                    InstanceProvider([]))
        binder.bind(guiinjectorkeys.DOCUMENT_MENU_ADDITIONS_KEY,
                    InstanceProvider([]))
        binder.bind(guiinjectorkeys.DOCUMENT_WINDOW_ADDITIONAL_REFERENCES_KEY,
                    InstanceProvider([]))
        binder.bind(guiinjectorkeys.EVENT_WINDOW_ADDITIONAL_REFERENCES_KEY,
                    InstanceProvider([]))

    # Windows
    @provider
    @singleton
    @inject
    def create_main_windows(self,
                            event_window: guiinjectorkeys.EVENT_WINDOW_KEY,
                            document_window: guiinjectorkeys.DOCUMENT_WINDOW_KEY,
                            document_base_reference_factories: guiinjectorkeys.DOCUMENT_WINDOW_BASE_REFERENCES_KEY,
                            document_additional_reference_factories: guiinjectorkeys.DOCUMENT_WINDOW_ADDITIONAL_REFERENCES_KEY,
                            event_base_reference_factories: guiinjectorkeys.EVENT_WINDOW_BASE_REFERENCES_KEY,
                            event_additional_reference_factories: guiinjectorkeys.EVENT_WINDOW_ADDITIONAL_REFERENCES_KEY) -> guiinjectorkeys.MAIN_WINDOWS_KEY:
        '''
        Returns a tuple of the application windows and thus forces
        the initialization of the windows
        Adding references must be done after instantiation, so it
        is done here.
        '''
        
        event_window.add_references(event_base_reference_factories + event_additional_reference_factories)
        document_window.add_references(document_base_reference_factories + document_additional_reference_factories)
        
        return (event_window, document_window)

    # References
    @provider
    @inject
    def get_document_base_references(
            self,
            document_event_reference: guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_FACTORY_KEY,
            document_file_reference: guiinjectorkeys.DOCUMENT_FILE_REFERENCES_FACTORY_KEY) -> guiinjectorkeys.DOCUMENT_WINDOW_BASE_REFERENCES_KEY:
        '''
        Returns an array of all reference widgets for documents.
        If you have plugins that define additional references,
        you have to overwrite this in your applications main module.
        '''
        return [document_event_reference, document_file_reference]
    
    @provider
    def get_document_additional_references(self) -> guiinjectorkeys.DOCUMENT_WINDOW_BASE_REFERENCES_KEY:
        '''
        Empty array. Will be overridden for plugins.
        '''
        return []

    @provider
    @inject
    def create_event_base_references(self,
                                event_cross_references: guiinjectorkeys.EVENT_CROSS_REFERENCES_FACTORY_KEY,
                                event_document_reference: guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_FACTORY_KEY,
                                event_type_reference: guiinjectorkeys.EVENT_TYPE_REFERENCES_FACTORY_KEY) -> guiinjectorkeys.EVENT_WINDOW_BASE_REFERENCES_KEY:
        '''
        Returns an array of all reference widgets for events.
        If you have plugins that define additional references,
        you have to overwrite this in your applications main module.
        '''
        return [event_cross_references, event_document_reference, event_type_reference]
    
    # Dialogs
    @provider
    @inject
    def create_document_dialogs(self,
                                documentid_selection_dialog: guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_KEY,
                                document_filter_dialog: guiinjectorkeys.DOCUMENT_FILTER_DIALOG_KEY) -> guiinjectorkeys.DOCUMENT_WINDOW_DIALOGS_KEY:
        '''
        Returns a dictionary of dialogs for the document window.
        '''
        return {
            BaseWindow.GOTO_DIALOG: documentid_selection_dialog,
            BaseWindow.FILTER_DIALOG: document_filter_dialog
            }
    
    @provider
    @inject
    def create_event_dialogs(self,
                             date_range_dialog: guiinjectorkeys.DATERANGE_SELECTION_DIALOG_KEY,
                             date_dialog: guiinjectorkeys.DATE_SELECTION_DIALOG_KEY,
                             event_filter_dialog: guiinjectorkeys.EVENT_FILTER_DIALOG_KEY,
                             confirm_new_event_dialog: guiinjectorkeys.EVENT_CONFIRMATION_DIALOG_KEY) -> guiinjectorkeys.EVENT_WINDOW_DIALOGS_KEY:
        '''
        Returns a dictionary of dialogs for the event window.
        '''
        return {
            EventWindow.DATE_RANGE_DIALOG: date_range_dialog,
            EventWindow.CONFIRM_NEW_EVENT_DIALOG: confirm_new_event_dialog,
            BaseWindow.GOTO_DIALOG: date_dialog,
            BaseWindow.FILTER_DIALOG: event_filter_dialog
            }

    @provider
    @inject
    def init_viewers(self, config: baseinjectorkeys.CONFIG_KEY) -> guiinjectorkeys.DOCUMENT_FILE_VIEWERS_KEY:
        '''
        Initializes the file viewers from the information
        given in the config.xml. The viewer may either be
        a class in the fileviewers module or an external
        program that is started with the file as first
        parameter.
        '''
        viewers = {}
        for (filetype, viewer) in config.filetypeviewers.items():
            try:
                viewers[filetype] = getattr(fileviewers, viewer)()
            except AttributeError:
                viewers[filetype] = ExternalViewer(viewer)
        
        return viewers
