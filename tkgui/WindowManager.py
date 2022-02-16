'''
Created on 15.02.2022

@author: michael
'''
from injector import inject
from alexpresenters.MessageBroker import MessageBroker, REQ_QUIT, Message,\
    REQ_SAVE_ALL
from tkgui.AlexWidgets import AlexTk
from tkinter import Toplevel
from threading import Thread

GOTO_DIALOG = 'goto_dialog'
FILTER_DIALOG = 'filter_dialog'
DATE_RANGE_DIALOG = 'new_date_range_dialog'
CONFIRM_NEW_EVENT_DIALOG = 'confirm_new_event_dialog'

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
    def __init__(self,
                 message_broker: MessageBroker):
        
        self.message_broker = message_broker
        self.message_broker.subscribe(self)

        self.windows = []
        self.threads = []
        self.root = AlexTk()
        # Won't be using the root window - this leads to
        # trouble
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    def create_new_window(self, title='Alexandria'):
        '''
        Returns a new toplevel window.
        '''
        window = Toplevel(self.root)
        window.title(title)
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
        