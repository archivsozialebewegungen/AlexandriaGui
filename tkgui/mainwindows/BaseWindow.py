'''
Created on 06.11.2015

@author: michael
'''
from tkinter import Tk, Frame, Button, Label, Toplevel
from PIL.ImageTk import PhotoImage
from tkinter.constants import LEFT, NW, NE, RAISED, X, RIGHT, TOP
from injector import singleton, inject
from tkgui import guiinjectorkeys

import Pmw
import os
from alexpresenters.mainwindows.BaseWindowPresenter import REQ_QUIT,\
    REQ_SAVE_ALL
from alexpresenters.messagebroker import Message
import sys
from tkgui.components.alexwidgets import AlexMessageBar

@singleton
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

    @inject(message_broker=guiinjectorkeys.MESSAGE_BROKER_KEY,
            setup_runner=guiinjectorkeys.SETUP_RUNNER_KEY)
    def __init__(self, message_broker, setup_runner):
        
        self.setup_runner = setup_runner
        self.message_broker = message_broker
        self.message_broker.subscribe(self)

        self.windows = []
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        # pylint: disable=no-member
        Pmw.initialise(self.root)  # @UndefinedVariable

    def create_new_window(self):
        '''
        Returns a new toplevel window.
        '''
        if len(self.windows) == 0:
            self.windows.append(self.root)
            return self.root
        
        else:
            window = Toplevel(self.root)
            window.protocol("WM_DELETE_WINDOW", self._quit)
            self.windows.append(window)
            return window

    def receive_message(self, message):
        '''
        Interface method for the message broker
        '''
        if message.key == REQ_QUIT:
            self._quit()
            
    def _quit(self):
        
        self.message_broker.send_message(Message(REQ_SAVE_ALL))
        self.root.quit()

    def run(self):
        self.root.after_idle(lambda: self.setup_runner.run(self.root))
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
    
    def __init__(self, window_manager, presenter, dialogs, reference_factories, plugins):
        
        self.window_manager = window_manager
        self.window = self.window_manager.create_new_window()
        
        super().__init__(self.window)
        
        self.presenter = presenter
        self.presenter.view = self
        
        self.dialogs = dialogs
        self.plugins = plugins
        
        self._entity = None
        self._entity_has_changed = False

        self._filter_expression = None
        
        self.icondir = self._get_icon_dir()

        self.references = []

        self._add_frames()
        self._add_references(reference_factories)
        self._add_message_bar()
        
        self.presenter.signal_window_ready()
        
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

        self._add_navigation_buttons(top)
        
    def _add_menu(self, parent):
        
        # pylint: disable=no-member
        self.menubar = Pmw.MenuBar(parent)  # @UndefinedVariable
        self.menubar.pack(side=LEFT, expand=1, fill=X, anchor=NW)

        self.menubar.addmenu(_('Records'), '')
        self.menubar.addmenuitem(_('Records'), 'command', '',
                                 label=_('First record'),
                                 command=self.presenter.goto_first)
        self.menubar.addmenuitem(_('Records'), 'command', '',
                                 label=_('Last record'),
                                 command=self.presenter.goto_last)
        self.menubar.addmenuitem(_('Records'), 'command', '',
                                 label=_('Next record'),
                                 command=self.presenter.goto_next)
        self.menubar.addmenuitem(_('Records'), 'command', '',
                                 label=_('Previous record'),
                                 command=self.presenter.goto_previous)
        self.menubar.addmenuitem(_('Records'), 'command', '',
                                 label=_('New record'),
                                 command=self.presenter.create_new)
        self.menubar.addmenuitem(_('Records'), 'command', '',
                                 label=_('Delete record'),
                                 command=self.presenter.delete)
        self.menubar.addmenuitem(_('Records'), 'command', '',
                                 label=_('Quit'),
                                 command=self.presenter.quit)

        self.menubar.addmenu(_('Navigation'), '')
        self.menubar.addmenuitem(_('Navigation'), 'command', '',
                                 label=_('Goto record'),
                                 command=self.presenter.goto_record)
        self.menubar.addmenuitem(_('Navigation'), 'command', '',
                                 label=_('Filtering'),
                                 command=self.presenter.toggle_filter)
        
        for plugin in self.plugins:
            plugin.attach_to_window(self)

    def _add_navigation_buttons(self, parent):

        self.iconframe = Frame(parent)
        self.iconframe.pack(side=LEFT, fill=X, anchor=NE, pady=1, padx=1)

        self.nexticon = PhotoImage(master=self.iconframe, file=os.path.join(self.icondir, 'next.gif'))
        self.previousicon = PhotoImage(master=self.iconframe, file=os.path.join(self.icondir, 'previous.gif'))
        self.firsticon = PhotoImage(master=self.iconframe, file=os.path.join(self.icondir, 'first.gif'))
        self.lasticon = PhotoImage(master=self.iconframe, file=os.path.join(self.icondir, 'last.gif'))
        self.newicon = PhotoImage(master=self.iconframe, file=os.path.join(self.icondir, 'new.gif'))

        Button(self.iconframe, image=self.firsticon, bd=1, relief=RAISED,
               command=self.presenter.goto_first).pack(side=LEFT, padx=2)
        Button(self.iconframe, image=self.previousicon, bd=1, relief=RAISED,
               command=self.presenter.goto_previous).pack(side=LEFT, padx=2)
        Button(self.iconframe, image=self.newicon, bd=1, relief=RAISED,
               command=self.presenter.create_new).pack(side=LEFT, padx=2)
        Button(self.iconframe, image=self.nexticon, bd=1, relief=RAISED,
               command=self.presenter.goto_next).pack(side=LEFT, padx=2)
        Button(self.iconframe, image=self.lasticon, bd=1, relief=RAISED,
               command=self.presenter.goto_last).pack(side=LEFT, padx=2)

    def _add_filter_warning(self, parent):
        
        self.filter_warning = Label(parent, text = "", foreground='red')
        self.filter_warning.pack(side=TOP)

    def _add_references(self, reference_factories):
        
        self.references_frame = Frame(self.window)
        self.references_frame.pack(side=TOP, anchor=NW)
        
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
        
    def _get_filter_expression(self):
        return self._filter_expression
    
    def _set_filter_expression(self, filter_expression):
        self._filter_expression = filter_expression
        if isinstance(filter_expression, type(None)):
            self.filter_warning.configure(text="")
        else:
            self.filter_warning.configure(text=_("Filter is set!"))
            self.presenter.goto_first()
        

    def _execute_dialog(self, dialog, *params, **kw):
        return self.dialogs[dialog].activate(self.window, *params, **kw)
    
    def _get_new_filter(self):
        return self._execute_dialog(self.FILTER_DIALOG)
        
    def _get_record_id_selection(self):
        return self._execute_dialog(self.GOTO_DIALOG)
        
        
    record_id_selection = property(_get_record_id_selection)
    filter_expression = property(_get_filter_expression, _set_filter_expression)
    new_filter = property (_get_new_filter)
    # This is kind of hackish because we want to be able to overwrite the setters
    # and getters in child classes
    entity = property(
        lambda self: self._view_to_entity(),
        lambda self, entity: self._entity_to_view(entity)
    )
