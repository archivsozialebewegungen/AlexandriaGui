'''
Created on 21.01.2018

@author: michael
'''
from tkinter import Frame, Toplevel
from tkinter.constants import LEFT, NW, X, RIGHT, TOP, WORD, DISABLED, NORMAL,\
    FLAT, CENTER
from injector import singleton, inject, Module, ClassProvider, InstanceProvider,\
    provider
from tkgui import _, guiinjectorkeys

import os
from alexpresenters.MessageBroker import Message, CONF_SETUP_FINISHED,\
    REQ_SAVE_ALL, REQ_QUIT
import sys
from tkgui.AlexWidgets import AlexMessageBar, AlexMenuBar, AlexTk,\
    AlexLabel, AlexText, AlexRadioGroup, AlexButton
from threading import Thread
from tkinter.ttk import Notebook

class WindowManager():
    '''
    This is the class that handles all different windows. It
    is itself a child of Tk and creates new windows on request.

    The window classes of the applicaton are just children of Frame,
    the request a Toplevel window to attach to from this WindowManager.
    The WindowManager will be injected into the window classes, these
    request a new Toplevel window from the window manager and
    attach themselves to this window.
    '''

    @inject
    @singleton
    def __init__(self,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY):
        
        self.message_broker = message_broker
        self.message_broker.subscribe(self)

        self.windows = []
        self.threads = []
        self.root = AlexTk()
        # Won't be using the root window - this leads to
        # trouble
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    def create_new_window(self):
        '''
        Returns a new toplevel window.
        '''
        window = Toplevel(self.root)
        window.protocol("WM_DELETE_WINDOW", self._quit)
        self.windows.append(window)
        return window

    def remove_window(self, window):
        self.windows.remove(window)
        window.destroy()

    def receive_message(self, message):
        '''
        Interface method for the message broker
        '''
        if message.key == REQ_QUIT:
            self._quit()
            
    def run_in_thread(self, target, args=()):
        thread = Thread(target=target, args=args)
        self.threads.append(thread)
        thread.start()

    def _quit(self):
        
        self.message_broker.send_message(Message(REQ_SAVE_ALL))
        for thread in self.threads:
            thread.join()
        self.root.quit()

    def run(self, setup_runner):
        self.root.after_idle(lambda: setup_runner.run(self.root))
        self.root.mainloop()
        
class BaseWindow(Frame):
    """
        This class handles a lot of the functionality of the
        main windows of the application that are not dependent
        on the record type: menus, navigation buttons, the references
        grid etc.
    
    """
    GOTO_DIALOG = 'goto_dialog'
    FILTER_DIALOG = 'filter_dialog'
    
    def __init__(self, window_manager, message_broker, presenter, dialogs, plugins):
        
        self.window_manager = window_manager
        self.window = self.window_manager.create_new_window()
        self.window.withdraw()
        
        message_broker.subscribe(self)
        
        super().__init__(self.window)
        
        self.presenter = presenter
        self.presenter.view = self
        
        self.dialogs = dialogs
        self.plugins = plugins
        
        self._entity = None
        self._entity_has_changed = False

        self.references = []
        self.new_record_id = None
        self.filter_object = None
        
        self._add_frames()

        self.references_frame = Frame(self.window)
        self.references_frame.pack(side=TOP, anchor=NW)
        
        self._add_message_bar()

    def receive_message(self, message):
        if message == CONF_SETUP_FINISHED:
            self.show_window()
        
    def show_window(self):
        
        self.window.deiconify()
        
    def _get_icon_dir(self):
        this_module = BaseWindow.__module__
        this_file = os.path.abspath(sys.modules[this_module].__file__)
        this_directory = os.path.dirname(this_file)
        return os.path.join(this_directory, 'Icons')
        
    def _add_frames(self):
        
        top = Frame(self.window)
        top.pack(fill=X, expand=1)

        self._add_menu(top)
        
        self._add_filter_warning(self.window)
        
        self.entity_frame = Frame(self.window)
        self.entity_frame.pack(side=TOP, anchor=NW)
        self._populate_entity_frame()

    def _add_menu(self, parent):
        
        # pylint: disable=no-member
        self.menubar = AlexMenuBar(parent)
        self.window.config(menu=self.menubar)

        self.menubar.addmenu(_('Records'), '')
        self.menubar.addmenuitem(_('Records'), 'command',
                                 label=_('First record'),
                                 command=self.presenter.goto_first)
        self.menubar.addmenuitem(_('Records'), 'command',
                                 label=_('Last record'),
                                 command=self.presenter.goto_last)
        self.menubar.addmenuitem(_('Records'), 'command',
                                 label=_('Next record'),
                                 command=self.presenter.goto_next)
        self.menubar.addmenuitem(_('Records'), 'command',
                                 label=_('Previous record'),
                                 command=self.presenter.goto_previous)
        self.menubar.addmenuitem(_('Records'), 'command',
                                 label=_('New record'),
                                 command=self._create_new)
        self.menubar.addmenuitem(_('Records'), 'command',
                                 label=_('Delete record'),
                                 command=self.presenter.delete)
        self.menubar.addmenuitem(_('Records'), 'command',
                                 label=_('Quit'),
                                 command=self.presenter.quit)

        self.menubar.addmenu(_('Navigation'))
        self.menubar.addmenuitem(_('Navigation'), 'command', 
                                 label=_('Goto record'),
                                 command=self._activate_record_dialog)
        self.menubar.addmenuitem(_('Navigation'), 'command',
                                 label=_('Filtering'),
                                 command=self._toggle_filter)

        icondir = self._get_icon_dir()

        self.menubar.addshortcut(imagefile=os.path.join(icondir, 'first.gif'),
                                 command=self.presenter.goto_first)
        self.menubar.addshortcut(imagefile=os.path.join(icondir, 'previous.gif'),
                                 command=self.presenter.goto_previous)
        self.menubar.addshortcut(imagefile=os.path.join(icondir, 'new.gif'),
                                 command=self._create_new)
        self.menubar.addshortcut(imagefile=os.path.join(icondir, 'next.gif'),
                                 command=self.presenter.goto_next)
        self.menubar.addshortcut(imagefile=os.path.join(icondir, 'last.gif'),
                                 command=self.presenter.goto_last)

        for plugin in self.plugins:
            plugin.attach_to_window(self)

    def _add_filter_warning(self, parent):
        
        self.filter_warning = AlexLabel(parent, text = "", foreground='red')
        self.filter_warning.pack(side=TOP)

    def add_references(self, reference_factories):
        
        side = RIGHT
        
        for factory in reference_factories:
            if side == RIGHT:
                row = Frame(self.references_frame)
                row.pack(side=TOP)
                side = LEFT
            else:
                side = RIGHT
            view = factory.get_view(row)
            self.references.append(view)
            view.pack(side=side, padx=5, pady=5)
    
    def _add_message_bar(self):
        
        message_frame = Frame(self.window)
        message_frame.pack(side=TOP, anchor=NW, fill=X, expand=1)
        message_bar = AlexMessageBar(message_frame)
        message_bar.pack(fill=X, expand=1)
        # TODO: inject message broker into windows
        self.presenter.message_broker.subscribe(message_bar)

    def entity_has_changed(self):
        if self._entity_has_changed:
            return True
        self._view_to_entity()
        return self._entity_has_changed
    
    def _populate_entity_frame(self):
        raise Exception("Implement in child class!")
    
    def _entity_to_view(self, entity):
        raise Exception("Implement in child class!")
            
    def _view_to_entity(self):
        raise Exception("Implement in child class!")
        
    def _execute_dialog(self, dialog, *params, **kw):
        return self.dialogs[dialog].activate(*params, **kw)
    
    def _toggle_filter(self):
        if self.filter_object is None:
            self.dialogs[self.FILTER_DIALOG].activate(self._activate_filter)
        else:
            self.filter_object = None
            self.presenter.update_filter_expression()
            self.filter_warning.configure(text="")
        
    def _activate_filter(self, filter_object):
        self.filter_object = filter_object
        self.presenter.update_filter_expression()
        self.filter_warning.configure(text=_("Filter is set!"))
        self.presenter.goto_first()
                
    def _activate_record_dialog(self):
        self.dialogs[self.GOTO_DIALOG].activate(self._goto_record)
        
    def _goto_record(self, record_id):
        self.new_record_id = record_id
        self.presenter.goto_record()
        
    # This is kind of hackish because we want to be able to overwrite the setters
    # and getters in child classes. Without lambda, it would use the methods
    # in the parent class
    entity = property(
        lambda self: self._view_to_entity(),
        lambda self, entity: self._entity_to_view(entity)
    )

class DocumentWindow(BaseWindow):
    '''
    The window for manipulating documents.
    '''
    @inject
    @singleton
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 presenter: guiinjectorkeys.DOCUMENT_WINDOW_PRESENTER_KEY,
                 dialogs: guiinjectorkeys.DOCUMENT_WINDOW_DIALOGS_KEY,
                 document_menu_additions: guiinjectorkeys.DOCUMENT_MENU_ADDITIONS_KEY):
        self.notebook = None
        self._description_widget = None
        self._condition_widget = None
        self._keywords_widget = None
        super().__init__(window_manager, message_broker, presenter, dialogs, document_menu_additions)

    def _create_new(self):
        self.presenter.create_new()
    
    def _change_widget_state(self, state):
        self._description_widget.configure(state=state)
        self._condition_widget.configure(state=state)
        self._keywords_widget.configure(state=state)
        
    def _clear_widgets(self):
        self._document_label.set(_("No document available"))
        self._description_widget.set('')
        self._condition_widget.set('')
        self._keywords_widget.set('')

    def _disable_widgets(self):
        self._change_widget_state(DISABLED)
        
    def _enable_widgets(self):
        self._change_widget_state(NORMAL)

    def _populate_entity_frame(self):
        # pylint: disable=no-member
        self._document_label = AlexLabel(self.entity_frame, text=_("No document available"))
        self._document_label.pack()
        self.notebook = Notebook(self.entity_frame)
        self.notebook.pack(fill=X)
        description = Frame(self.notebook)
        self.notebook.add(description, text=_('Description'))
        self._description_widget = AlexText(description,
                                 font="Helvetica 12 bold",
                                 wrap=WORD,
                                 height=6)
        self._description_widget.pack(fill=X)
        condition = Frame(self.notebook)
        self.notebook.add(condition, text=_('Condition'))
        self._condition_widget = AlexText(condition,
                                 font="Helvetica 12 bold",
                                 wrap=WORD,
                                 height=6)
        self._condition_widget.pack(fill=X)
        keywords = Frame(self.notebook)
        self.notebook.add(keywords, text=_('Keywords'))
        self._keywords_widget = AlexText(keywords,
                                 font="Helvetica 12 bold",
                                 wrap=WORD,
                                 height=6)
        self._keywords_widget.pack(fill=X)

    def _view_to_entity(self):
        if self._entity == None:
            return None

        if self._description_widget.get() != self._entity.description:
            self._entity_has_changed = True
            self._entity.description = self._description_widget.get()
        if self._condition_widget.get() != self._entity.condition:
            self._entity_has_changed = True
            self._entity.condition = self._condition_widget.get()
        if self._keywords_widget.get() != self._entity.keywords:
            self._entity_has_changed = True
            self._entity.keywords = self._keywords_widget.get()
        
        return self._entity
    
    def _entity_to_view(self, entity):
        
        if self._entity != entity:
            self._entity_has_changed = False
            
        if self._entity == None:
            self._enable_widgets()

        self._entity = entity
        if entity == None:
            self._clear_widgets()
            self._disable_widgets()
            return
        
        if self._entity.id == None:
            self._document_label.set(_("New document"))
        else:
            self._document_label.set(_("Document no.{0:d} ({1!s})").format(self._entity.id, self._entity.document_type.description))
        self._description_widget.set(self._entity.description)
        self._condition_widget.set(self._entity.condition)
        self._keywords_widget.set(self._entity.keywords)

class EventProxy:
    
    def __init__(self, view, event):
        
        self.event = event
        self.view = view
        
    def _is_attached(self):
        return self.id == self.view._entity.id
    
    def _get_id(self):
        return self.event.id
    
    def _set__id(self, event_id):
        self.event._id = event_id

    def _get_erfasser(self):
        return self.event.erfasser
    
    def _set_erfasser(self, erfasser):
        self.event.erfasser = erfasser
            
    def _get_daterange(self):
        return self.event.daterange
    
    def _set_daterange(self, daterange):
        self.event.daterange = daterange
        if self._is_attached():
            self.view._daterange_widget.set(daterange)
            
    def _get_description(self):
        return self.event.description
    
    def _set_description(self, description):
        self.event.description = description
        if self._is_attached():
            self.view._description_widget.set(description)
            
    def _get_status_id(self):
        return self.event.status_id
    
    def _set_status_id(self, status_id):
        self.event.status_id = status_id
        if self._is_attached():
            self.view._status_widget.set(status_id)
            
    def _get_location_id(self):
        return self.event.location_id        
            
    def _set_location_id(self, location_id):
        self.event.location_id = location_id
        if self._is_attached():
            self.view._location_widget.set(location_id)
            
    id = property(_get_id)
    _id = property(_get_id, _set__id)
    erfasser = property(_get_erfasser, _set_erfasser)
    daterange = property(_get_daterange, _set_daterange)
    description = property(_get_description, _set_description)
    status_id = property(_get_status_id, _set_status_id)
    location_id = property(_get_location_id, _set_location_id)
    
class EventWindow(BaseWindow):
    
    DATE_RANGE_DIALOG = 'new_date_range_dialog'
    CONFIRM_NEW_EVENT_DIALOG = 'confirm_new_event_dialog'

    @inject
    @singleton
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 message_broker: guiinjectorkeys.MESSAGE_BROKER_KEY,
                 presenter: guiinjectorkeys.EVENT_WINDOW_PRESENTER_KEY,
                 dialogs: guiinjectorkeys.EVENT_WINDOW_DIALOGS_KEY,
                 event_menu_additions: guiinjectorkeys.EVENT_MENU_ADDITIONS_KEY):
        super().__init__(window_manager, message_broker, presenter, dialogs, event_menu_additions)
        self.date_range_for_new_event = None

    def _create_new(self):
        '''
        Creating a new event involves quit a lot of user interaction.
        First a dialog needs to pop up for entering a data range.
        If this dialog is closed, it is necessary to check if there
        are already events for this date. If so, another dialog needs
        to be shown where the user can decide, if she wants to go to
        one of the already existing events or if she really wants
        to create a new event for the given date range.
        '''
        self.dialogs[self.DATE_RANGE_DIALOG].activate(self._activate_create_new)
        
    def _activate_create_new(self, value):
        '''
        Callback for the creation of a new event.
        '''
        if value == None:
            return
        
        self.date_range_for_new_event = value
        self.presenter.fetch_events_for_new_event_date()
        
    def _select_from_event_list(self, event_list):
        '''
        This is (implicitely) called from the
        fetch_events_for_new_event_date() in the presenter.
        If there is no other event for the given date range,
        create a new event. Otherwise open a dialog to
        either select one of the existing events or confirm
        that a new event needs to be created.
        '''
        if len(event_list) == 0:
            self.presenter.create_new()
        else:
            self.dialogs[self.CONFIRM_NEW_EVENT_DIALOG].activate(self._confirm_new_event_callback,
                                                                 event_list=event_list,
                                                                 date=self.date_range_for_new_event.start_date)
    
    def _confirm_new_event_callback(self, value):
        if value == None:
            # None of the existing events has been selected
            self.presenter.create_new_event()
        else:
            self._goto_record(value.id)
        
    def _change_date_range(self):
        self.dialogs[self.DATE_RANGE_DIALOG].activate(self._activate_change_date)

    def _activate_change_date(self, value):
        self.new_date_range = value
        self.presenter.change_event_date()

    def _populate_entity_frame(self):
        
        self._add_daterange()
        self._add_description()
        self._add_helpers()
        
    def _change_widget_state(self, new_state):
        self._daterange_widget.configure(state=new_state)
        self._description_widget.configure(state=new_state)
        self._location_widget.state = new_state
        self._status_widget.state = new_state
        
    def _clear_widgets(self):
        self._daterange_widget.set(_("No event to display!"))
        self._description_widget.set('')
        self._location_widget.set(False)
        self._status_widget.set(False)
        
    def _disable_widgets(self):
        self._change_widget_state(DISABLED)
        
    def _enable_widgets(self):
        self._change_widget_state(NORMAL)

    def _add_daterange(self):
       
        self._daterange_widget = AlexButton(self.entity_frame,
                                  relief=FLAT,
                                  command=self._change_date_range,
                                  state=DISABLED)
        self._daterange_widget.pack(side=TOP, padx=5, pady=5, anchor=CENTER)

    def _add_description(self):
       
        self._description_widget = AlexText(self.window,
                                 font="Helvetica 12 bold",
                                 wrap=WORD,
                                 height=6,
                                 width=60,
                                 state=DISABLED)
        self._description_widget.pack()
        
    def _add_helpers(self):
        helper_frame = Frame(self.window)
        helper_frame.pack(anchor=NW)
        self._add_location_chooser(helper_frame)
        self._add_status_chooser(helper_frame)

    def _add_location_chooser(self, helper_frame):
        location_texts = [_('not registered'), _('local'), _('countrywide'), _('national'), _('international')]
        self._location_widget = AlexRadioGroup(helper_frame, choices=location_texts, title=_('Location'))
        self._location_widget.pack(side=LEFT, anchor=NW, padx=5, pady=5)
                        
    def _add_status_chooser(self, helper_frame):
        status_texts = [_('unconfirmed'), _('probable'), _('confirmed')]
        self._status_widget = AlexRadioGroup(helper_frame, choices=status_texts, title=_('State'))
        self._status_widget.pack(side=LEFT, anchor=NW, padx=5, pady=5)
    
    def _entity_to_view(self, entity):
        
        self._new_date_range = None
        self._entity_has_changed = False
        
        if self._entity == None:
            self._enable_widgets()
        
        if entity == None:
            self._entity = None
            self._clear_widgets()
            self._disable_widgets()
            return

        if isinstance(entity, EventProxy):
            # Already wrapped
            self._entity = entity
        else:
            # Fresh entity
            self._entity = EventProxy(self, entity)
        
        self._daterange_widget.set(self._entity.daterange)
        self._description_widget.set(self._entity.description)
        self._location_widget.set(self._entity.location_id)
        self._status_widget.set(self._entity.status_id)
    
    def _view_to_entity(self):
        if self._entity == None:
            return None
        if self._description_widget.get() != self._entity.description:
            self._entity_has_changed = True
            self._entity.description = self._description_widget.get()
        if self._location_widget.get() != self._entity.location_id:
            self._entity_has_changed = True
            self._entity.location_id = self._location_widget.get()
        if self._status_widget.get() != self._entity.status_id: 
            self._entity_has_changed = True
            self._entity.status_id = self._status_widget.get()
        return self._entity

    event_list = property(None, _select_from_event_list)
    
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
                             event_id_dialog: guiinjectorkeys.EVENT_ID_SELECTION_DIALOG_KEY,
                             event_filter_dialog: guiinjectorkeys.EVENT_FILTER_DIALOG_KEY,
                             confirm_new_event_dialog: guiinjectorkeys.EVENT_CONFIRMATION_DIALOG_KEY) -> guiinjectorkeys.EVENT_WINDOW_DIALOGS_KEY:
        '''
        Returns a dictionary of dialogs for the event window.
        '''
        return {
            EventWindow.DATE_RANGE_DIALOG: date_range_dialog,
            EventWindow.CONFIRM_NEW_EVENT_DIALOG: confirm_new_event_dialog,
            BaseWindow.GOTO_DIALOG: event_id_dialog,
            BaseWindow.FILTER_DIALOG: event_filter_dialog
            }
    