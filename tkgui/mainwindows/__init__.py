'''
Window module
'''
from injector import Module, ClassProvider, singleton, provides, inject
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

    # Windows
    @provides(guiinjectorkeys.MAIN_WINDOWS_KEY, scope=singleton)
    @inject(event_window=guiinjectorkeys.EVENT_WINDOW_KEY,
            document_window=guiinjectorkeys.DOCUMENT_WINDOW_KEY)
    def create_main_windows(self, event_window, document_window):
        '''
        Returns a tuple of the application windows and thus forces
        the initialization of the windows
        '''
        return (event_window, document_window)

    # References
    @provides(guiinjectorkeys.DOCUMENT_WINDOW_REFERENCES_KEY)
    @inject(document_event_reference=guiinjectorkeys.DOCUMENT_EVENT_REFERENCES_FACTORY_KEY)
    @inject(document_file_reference=guiinjectorkeys.DOCUMENT_FILE_REFERENCES_FACTORY_KEY)
    def get_document_references(
            self,
            document_event_reference,
            document_file_reference):
        '''
        Returns an array of all reference widgets for documents.
        '''
        return [document_event_reference, document_file_reference]
    
    @provides(guiinjectorkeys.EVENT_WINDOW_REFERENCES_KEY)
    @inject(event_cross_references=guiinjectorkeys.EVENT_CROSS_REFERENCES_FACTORY_KEY)
    @inject(event_document_reference=guiinjectorkeys.EVENT_DOCUMENT_REFERENCES_FACTORY_KEY)
    @inject(event_type_reference=guiinjectorkeys.EVENT_TYPE_REFERENCES_FACTORY_KEY)
    def create_event_references(self,
                                event_cross_references,
                                event_document_reference,
                                event_type_reference):
        '''
        Returns an array of all reference widgets for events.
        '''
        return [event_cross_references, event_document_reference, event_type_reference]
    
    # Dialogs
    @provides(guiinjectorkeys.DOCUMENT_WINDOW_DIALOGS_KEY)
    @inject(documentid_selection_dialog=guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_KEY,
            document_filter_dialog=guiinjectorkeys.DOCUMENT_FILTER_DIALOG_KEY)
    def create_document_dialogs(self, documentid_selection_dialog, document_filter_dialog):
        '''
        Returns a dictionary of dialogs for the document window.
        '''
        return {
            BaseWindow.GOTO_DIALOG: documentid_selection_dialog,
            BaseWindow.FILTER_DIALOG: document_filter_dialog
            }
    
    @provides(guiinjectorkeys.EVENT_WINDOW_DIALOGS_KEY)
    @inject(date_range_dialog=guiinjectorkeys.DATERANGE_SELECTION_DIALOG_KEY,
            date_dialog=guiinjectorkeys.DATE_SELECTION_DIALOG_KEY,
            event_filter_dialog=guiinjectorkeys.EVENT_FILTER_DIALOG_KEY,
            confirm_new_event_dialog=guiinjectorkeys.EVENT_CONFIRMATION_DIALOG_KEY)
    def create_event_dialogs(self,
                             date_range_dialog,
                             date_dialog,
                             event_filter_dialog,
                             confirm_new_event_dialog):
        '''
        Returns a dictionary of dialogs for the event window.
        '''
        return {
            EventWindow.DATE_RANGE_DIALOG: date_range_dialog,
            EventWindow.CONFIRM_NEW_EVENT_DIALOG: confirm_new_event_dialog,
            BaseWindow.GOTO_DIALOG: date_dialog,
            BaseWindow.FILTER_DIALOG: event_filter_dialog
            }

    @provides(guiinjectorkeys.DOCUMENT_FILE_VIEWERS_KEY)
    @inject(config=baseinjectorkeys.CONFIG_KEY)
    def init_viewers(self, config):
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
