from tkgui.components.alexwidgets import AlexEntry, AlexButton, AlexLabel,\
    AlexDateEntry, AlexMessageBar, AlexComboBox, AlexListBox
from tkinter.ttk import Button
from tkinter.constants import TOP, BOTH, TRUE
from alexandriabase.domain import InvalidDateException
from alexpresenters.messagebroker import MessageBroker, ERROR_MESSAGE, Message
from manual.manual_tester import AbstractComponentTest, TestRunner

class AlexDateEntryTest(AbstractComponentTest):
    
    def __init__(self):
        super().__init__()
        self.name = "Date entry widget"
        
    def test_component(self, master, message_label):
        super().test_component(master, message_label)
        self.entry_widget = AlexDateEntry(self.master)
        self.entry_widget.pack(side=TOP, fill=BOTH, expand=TRUE)
        Button(self.master,
               text="Get entry",
               command=self._show_result).pack(side=TOP)

    def _show_result(self):
        try:
            date = self.entry_widget.get()
            self.message_label.set(date)
        except InvalidDateException as e:
            self.message_label.set(e)
            


class AlexLabelTest(AbstractComponentTest):

    def __init__(self):
        super().__init__()
        self.name = "Alex label test"

    def test_component(self, master, message_label):

        self.message_label = message_label
        self.master = master
        
        self.label1 = AlexLabel(master)
        self.label1.set('Label text:')
        self.label1.grid(row=0, column=0)
        
        self.entry1 = AlexEntry(master)
        self.entry1.set("Enter label text")
        self.entry1.grid(row=0, column=1)

        Button(master, text='Set label text', command=self._set_label_text).grid(row=1, column=0)
        Button(master, text='Set entry from label', command=self._set_entry_from_label).grid(row=1, column=1)
        
    def _set_label_text(self):
        
        self.label1.set(self.entry1.get())
        self.entry1.set('')
        
    def _set_entry_from_label(self):
        
        self.entry1.set(self.label1.get())

class AlexEntryTest(AbstractComponentTest):
    
    def __init__(self):
        super().__init__()
        self.name = "Alex entry test"

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.master = master
        
        label1 = AlexLabel(master)
        label1.set('Entry 1:')
        label1.grid(row=0, column=0)
        
        self.entry1 = AlexEntry(master)
        self.entry1.set("Entry 1 text")
        self.entry1.grid(row=0, column=1)
        
        label2 = AlexLabel(master)
        label2.set('Entry 2:')
        label2.grid(row=1, column=0)

        self.entry2 = AlexEntry(master)
        self.entry2.set("Entry 2 text")
        self.entry2.grid(row=1, column=1)
        
        Button(master, text='Switch input', command=self._switch_input).grid(row=2, column=1)
        
    def _switch_input(self):
        
        tmp = self.entry1.get()
        self.entry1.set(self.entry2.get())
        self.entry2.set(tmp)

class AlexMessageBarTest(AbstractComponentTest):
    '''
    Test class to test the working of the widget. The systematic_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the presenter.
    '''

    def __init__(self):
        super().__init__()
        self.message_broker = MessageBroker()
        self.name = "Message bar"

    def create_view(self, master):
        self.message_bar = AlexMessageBar(master,)
        self.message_broker.subscribe(self.message_bar)
        self.message_bar.pack(side=TOP)
        
    def add_button(self, master):

        message = Message(ERROR_MESSAGE, messagetype='error', message='An error has occurred')
        button = Button(master, text='Send error message',
                                command=lambda m=message: self.message_broker.send_message(m))
        button.pack(side=TOP)

    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_view(master)
        self.add_button(master)

class AlexComboBoxTest(AbstractComponentTest):
    '''
    Test class to test the working of the widget. The systematic_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the presenter.
    '''

    def __init__(self):
        super().__init__()
        self.name = "Combo box"

    def create_view(self, master):
        
        self.combobox = AlexComboBox(master)
        self.combobox.pack()
        
        self.button = Button(master, text="Add item", command=self.add_item)
        self.button.pack()
        
    def add_item(self):
        
        items = self.combobox.get_items()
        items.append("item%d" % (len(items) + 1))
        self.combobox.set_items(items)
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_view(master)
        
class AlexListBoxTest(AbstractComponentTest):
    '''
    Test class to test the working of the widget. The systematic_references_presenter is
    initialized with mock implementations of the dependencies. There
    should also be a an integration test for the presenter.
    '''

    def __init__(self):
        super().__init__()
        self.name = "List box"

    def create_view(self, master):
        
        self.listbox = AlexListBox(master, selectioncommand=self.callback)
        self.listbox.pack()
        
        Button(master, text="Add item", command=self.add_item).pack()
        Button(master, text="Show selection", command=self.show_selection).pack()
        Button(master, text="Select third", command=self.select_third).pack()
        
    def callback(self, item):
        
        self.message_label.set(item)
        
    def add_item(self):
        
        items = self.listbox.get_items()
        text = "item" * len(items)
        items.append("%s%d" % (text, (len(items) + 1)))
        self.listbox.set_items(items)
        
    def show_selection(self):
        self.message_label.set(self.listbox.get())
        
    def select_third(self):
        
        items = self.listbox.get_items()
        if len(items) < 3:
            return
        self.listbox.set(items[2])
        
        
    def test_component(self, master, message_label):
        self.message_label = message_label
        self.create_view(master)
        

if __name__ == '__main__':
    test_classes = []
    test_classes.append(AlexDateEntryTest)
    test_classes.append(AlexLabelTest)
    test_classes.append(AlexEntryTest)
    test_classes.append(AlexMessageBarTest)
    test_classes.append(AlexComboBoxTest)
    test_classes.append(AlexListBoxTest)
    test_runner = TestRunner(test_classes)
    test_runner.run()
