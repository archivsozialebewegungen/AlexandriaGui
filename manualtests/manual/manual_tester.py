'''
Created on 22.01.2016

@author: michael
'''
from tkinter import Button, Frame
from tkinter.constants import LEFT, TOP, BOTH, SOLID, TRUE, NW
from alexpresenters.messagebroker import MessageBroker
from tkgui.components.alexwidgets import AlexLabel, AlexListBox
from tkgui.MainWindows import WindowManager

class AbstractComponentTest:
    
    def __init__(self):
        self.message_broker = MessageBroker()
        self.message_broker.subscribe(self)
        self.name = "Please overwrite name in subclass"
        
    def test_component(self, master, message_label):
        self.master = master
        self.message_label = message_label
        
    def __str__(self):
        return self.name

class TestRunner:
    
    def __init__(self, test_classes):
        
        self.message_broker = MessageBroker()
        self.window_manager = WindowManager(self.message_broker)

        self.create_test_instances(test_classes)
        
        self.root = self.window_manager.create_new_window()
        geometry = '800x450'
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
        self.menu_frame.pack(side=LEFT, anchor=NW, padx=5)
        
        label = AlexLabel(self.menu_frame)
        label.set("Select a test")
        label.pack()
        
        self.tests = AlexListBox(
            self.menu_frame,  # @UndefinedVariable
            height=len(self.test_instances),
            selectioncommand=self.run_selected_test,
        )

        self.tests.set_items(self.test_instances)        
        self.tests.pack(anchor=NW)
        
        self.widget_frame = Frame(top_frame, borderwidth=1, relief=SOLID)
        self.widget_frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
        
        quit_button = Button(button_frame, command=self.root.quit, text="Quit")
        quit_button.pack(side=LEFT)
        
    def create_test_instances(self, test_classes):

        self.test_instances = []
        for test_class in test_classes:
            self.test_instances.append(test_class())
        
    def run_selected_test(self, test):
        
        self.message_label.set("")
        if self.test_frame:
            self.test_frame.destroy()
        self.test_frame = Frame(self.widget_frame)
        self.test_frame.pack(padx=10, pady=10)
        test.test_component(self.test_frame, self.message_label)
        
    def run(self):
        
        self.root.mainloop()

