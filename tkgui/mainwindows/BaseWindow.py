'''
Created on 06.11.2015

@author: michael
'''
from tkinter import Frame, Toplevel
from tkinter.constants import LEFT, NW, X, RIGHT, TOP
from injector import singleton, inject
from tkgui import guiinjectorkeys

import os
from alexpresenters.messagebroker import Message, CONF_SETUP_FINISHED,\
    REQ_SAVE_ALL, REQ_QUIT
import sys
from tkgui.components.alexwidgets import AlexMessageBar, AlexMenuBar, AlexTk,\
    AlexLabel
from threading import Thread
import Pmw

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
        # pylint: disable=no-member
        Pmw.initialise(self.root)  # @UndefinedVariable

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
        parent_directory = os.path.dirname(this_directory)
        return os.path.join(parent_directory, 'Icons')
        
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
