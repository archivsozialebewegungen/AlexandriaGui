'''
Created on 22.01.2016

@author: michael
'''
from tkinter import Button, Frame, Tk
from tkinter.constants import LEFT, TOP, END, BOTH, SOLID, TRUE
import Pmw
from alexpresenters.messagebroker import MessageBroker, REQ_SET_EVENT, Message,\
    CONF_EVENT_CHANGED, REQ_SET_DOCUMENT, CONF_DOCUMENT_CHANGED, ERROR_MESSAGE
from tkgui.components.alexwidgets import AlexLabel

class AbstractComponentTest:
    
    def __init__(self):
        self.message_broker = MessageBroker()
        self.message_broker.subscribe(self)
        self.name = "Please overwrite name in subclass"
        
    def receive_message(self, message):
        if message == REQ_SET_EVENT:
            self.message_broker.send_message(Message(CONF_EVENT_CHANGED, event=message.event))
        if message == REQ_SET_DOCUMENT:
            self.message_broker.send_message(Message(CONF_DOCUMENT_CHANGED, document=message.document))
        if message == CONF_EVENT_CHANGED:
            self.message_label.set("Current event: %s" % message.event)
        if message == CONF_DOCUMENT_CHANGED:
            self.message_label.set("Current document: %s" % message.document)
        if message == ERROR_MESSAGE:
            self.message_label.set(message.message)
        
    def test_component(self, master, message_label):
        self.master = master
        self.message_label = message_label

class TestRunner:
    
    def __init__(self, test_classes):
        self.test_classes = test_classes
        self.root = Tk()
        geometry = '800x300'
        self.root.geometry(geometry)
        
        self.test_frame = None
        
        top_frame = Frame(self.root)
        top_frame.pack(side=TOP, fill=BOTH, expand=TRUE)
        
        message_frame = Frame(self.root)
        message_frame.pack(side=TOP)
        
        button_frame = Frame(self.root)
        button_frame.pack(side=TOP)
        
        self.message_label = AlexLabel(message_frame)
        self.message_label.pack(side=LEFT)
        
        self.menu_frame = Frame(top_frame)
        self.menu_frame.pack(side=LEFT, padx=5)
        
        self.tests = Pmw.ScrolledListBox(self.menu_frame,  # @UndefinedVariable
                labelpos='nw',
                label_text='Available components',
                listbox_height = 6,
                selectioncommand=self.run_selected_test,
                usehullsize = 1,
                hull_width = 200,
                hull_height = 250,
        )
        
        for test_class in self.test_classes:
            self.tests.insert(END, test_class.name)
        self.tests.pack()
        
        self.widget_frame = Frame(top_frame, borderwidth=1, relief=SOLID)
        self.widget_frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
        
        quit_button = Button(button_frame, command=self.root.quit, text="Quit")
        quit_button.pack(side=LEFT)
        
    def run_selected_test(self):
        
        self.message_label.set("")
        test_name = self.tests.getcurselection()[0]
        test = self.find_test(test_name)
        if not test:
            return
        if self.test_frame:
            self.test_frame.destroy()
        self.test_frame = Frame(self.widget_frame)
        self.test_frame.pack(padx=10, pady=10)
        test.test_component(self.test_frame, self.message_label)
        
    def find_test(self, test_name):
        tests = [x for x in self.test_classes if x.name == test_name]
        if len(tests) > 0:
            return tests[0]
        else:
            return None
        
    def run(self):
        
        self.root.mainloop()

