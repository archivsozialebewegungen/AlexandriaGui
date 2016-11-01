'''
Created on 21.11.2015

This module mostly wrapy tkinter widgets to get them a
uniform interface: get() and set(). For text widgets,
get always returns an empty string and this also is what
gui classes should return. Conversion and interpretation
should always be done in persenter classes. The view has
to be as stupid as possible.

Higher level widgets (for example for date entry) may
return None, if the widgets input fields are empty and
the expected object can't be properly initialized.

@author: michael
'''
# pylint: disable=too-many-ancestors
# pylint: disable=arguments-differ

from tkinter import Text, Button, StringVar, Frame, IntVar, Label, Radiobutton,\
    Entry, Checkbutton
from tkinter.constants import END, DISABLED, W, LEFT, NORMAL
from alexandriabase.domain import AlexDate
import Pmw
from idlelib.TreeWidget import TreeItem, TreeNode

class DateEntryFrame(Frame):
    # pylint: disable=too-many-ancestors
    '''
    A simple widget just to enter dates - without any validation
    '''

    def __init__(self, parent, label=_('Date'), labelwidth=15):
        Frame.__init__(self, parent)

        Label(self, text=label, width=labelwidth).pack(side=LEFT)
        self.day_entry = AlexEntry(self,width=2)
        self.day_entry.pack(side=LEFT)

        Label(self, text='.').pack(side=LEFT)
        self.month_entry = AlexEntry(self,width=2)
        self.month_entry.pack(side=LEFT)

        Label(self, text='.').pack(side=LEFT)
        self.year_entry = AlexEntry(self,width=4)
        self.year_entry.pack(side=LEFT)

    day = property(lambda self: self.day_entry.get(),
                   lambda self, value: self.day_entry.set(value))
    month = property(lambda self: self.month_entry.get(),
                     lambda self, value: self.month_entry.set(value))
    year = property(lambda self: self.year_entry.get(),
                    lambda self, value: self.year_entry.set(value))

class AlexDateEntry(DateEntryFrame):
    '''
    Widget to input an Alexandria date object. Day and
    month may be empty, but not the year. If something
    other than a number is entered, the field is simply
    treated as empty (and in fact set to empty, if the
    value is fetched).
    
    If the date is invalid, an InvalidDateException is thrown.
    '''
    
    def set(self, alex_date):
        '''
        Sets the date value. None is allowed to clear the
        input fields.
        '''
        if alex_date == None:
            self.day = None
            self.month = None
            self.year = None
        else:
            self.day = alex_date.day
            self.month = alex_date.month
            self.year = alex_date.year
            
    def get(self):
        '''
        Gets an AlexDate. Non integer input is silently ignored.
        If the year is empty, None is returned. If the date
        is not a valid AlexDate, an InvalidDateException is
        thrown.
        '''
        year_as_int = None
        month_as_int = None
        day_as_int = None
        try:
            year_as_int = int(self.year)
        except ValueError:
            self.year = ''
        try:
            month_as_int = int(self.month)
        except ValueError:
            self.month = ''
        try:
            day_as_int = int(self.day)
        except ValueError:
            self.day = ''
        if self.year == '':
            return None
        return AlexDate(year_as_int, month_as_int, day_as_int)

class AlexLabel(Label):
    '''
    Wraps the tkinter.Label class.
    '''
    
    def set(self, text):
        '''
        Sets the text as given. The input does not need to be
        a string: Other values or objects are converted to a
        string.
        '''
        self.configure(text="%s" % text)
        
    def get(self):
        '''
        Returns the value as string, stripped of leading and
        trailing blanks.
        '''
        return self.config()['text'][-1].strip()

class AlexText(Text):
    '''
    A multiline text field, wraps the tkinter.Text widget.
    Really expects text.
    '''
    # pylint disable=arguments-differ
    
    def set(self, text):
        '''
        Sets the text given. Should really be a string.
        '''
        self.delete('0.1', END)
        if text:
            self.insert(END, text)

    def get(self):
        '''
        Return the text entered into the widget. If there
        is a trailing newline, it will be removed.
        '''
        text = super().get('0.1', END)
        # Remove trailing linebreak added by widget
        if len(text) > 0 and text[-1:] == "\n":
            text = text[:-1]
        text = text.strip()
        return text

class AlexEntry(Entry):
    '''
    Wrapper arount tkinter entry widget.
    '''
    
    def __init__(self, *params, **kw):
        super().__init__(*params, **kw)
        
    def set(self, value):
        '''
        Sets the value into the widget. If it is not
        a string, it will be converted to a string.
        '''
        self.delete(0, END)
        if value == None:
            return
        text = "%s" % value
        self.insert(0, text.strip())
        
    def get(self):
        '''
        Returns the value of the entry, stripped of
        leading and trailing whitespaces.
        '''
        return super().get().strip()
        
class AlexButton(Button):
    '''
    Wrapper around the tkinter Button class
    '''
    
    def __init__(self, *params, **kw):
        self.textvar = StringVar()
        super().__init__(*params, textvariable=self.textvar, **kw)
        
    def set(self, value):
        '''
        Converts the value to string, strips it of leading and
        trailing whitspaces and sets it as button value.
        '''
        text = "%s" % value
        self.textvar.set(text.strip())
        
    def get(self):
        '''
        Returns the text of the button, stripped of leading and
        trailing whitspaces.
        '''
        return self.textvar.get().strip()
    
class AlexCheckBox(Checkbutton):
    '''
    Wrapper around the tkintr Checkbutton class.
    '''        
        
    def __init__(self, *params, **kw):
        self.int_var = IntVar()
        kw['variable'] = self.int_var
        super().__init__(*params, **kw)
            
    def set(self, booleanvalue):
        '''
        Ticks or unticks the checkbox according to the
        booleanvalue given.
        '''
        if booleanvalue:
            self.int_var.set(1)
        else:
            self.int_var.set(0)
                
    def get(self):
        '''
        If the box is ticked, returns True, else False.
        '''
        if self.int_var.get() == 0:
            return False
        else:
            return True

class AlexRadioGroup(Frame):
    '''
    Creates a radio group. Choices and title are given
    as parameters in the constructor.
    '''
        
    def __init__(self, *params, choices=[], title="", **kw):
        super().__init__(*params, **kw)
        self.intvar = IntVar()
        Label(self, text=title).pack(padx=5, pady=5)
        self.widgets = []
        for i in range(0,len(choices)):
            self.widgets.append(
                    Radiobutton(self,
                        text=choices[i],
                        value=i,
                        variable = self.intvar,
                        state = DISABLED))
            self.widgets[-1].pack(anchor=W)
        self.state = NORMAL

    def set(self, index):
        '''
        Sets the radio button with the given index.
        '''
        self.intvar.set(index)
        
    def get(self):
        '''
        Returns the index of the selected choice.
        '''
        return self.intvar.get()
    
    def _set_state(self, state):
        '''
        Setter to en-/disable the whole widget
        '''
        for widget in self.widgets:
            widget.configure(state=state)
            
    state = property(None, _set_state)

class AlexMessageBar(Pmw.MessageBar):  # @UndefinedVariable
    '''
    This subclasses the Pmw.MessageBar
    
    It displays all messages sent by the message broker that have
    the attributes 'messagetype' and 'message'. 'messagetype' may
    be error, warning, info and debug.
    It is possible to configure which alexandria messages should be
    shown using the method config_messages which expects a message key.
    If this configuration is used, only the messages configured
    will be shown.
    '''
    def __init__(self, *params, **kw):
        if 'messagetypes' not in kw:
            kw['messagetypes'] = {
                'error'   : (5, 10, 2, 1),
                'warning' : (4, 5, 1, 0),
                'info'    : (3, 5, 0, 0),
                'debug'   : (2, 5, 0, 0),
            }
        super().__init__(*params, **kw)
        self.messages = []
    
    def config_messages(self, message_key):
        self.messages.append(message_key)
        
    def receive_message(self, message):
        if len(self.messages) == 0 or message in self.messages:
            if hasattr(message, 'messagetype') and hasattr(message, 'message'):
                self.message(message.messagetype, message.message)

class AlexComboBoxDialog(Pmw.ComboBoxDialog):  # @UndefinedVariable
    
    def __init__(self, *params, **kw):
        self.objects = {}
        for item in kw['scrolledlist_items']:
            self.objects['%s' % item] = item
        super().__init__(*params, **kw)
        
    def get(self):
        key = super().get()
        if key == None or key == '':
            return None
        return self.objects[key]

class AlexTreeItem(TreeItem):

    def __init__(self, node):
    
        self.node = node
        
    def GetText(self):
        return "%s" % self.node

    def IsExpandable(self):
        return len(self.node.children) > 0

    def GetSubList(self):
        items = []
        for child_node in self.node.children:
            if child_node.visible:
                items.append(AlexTreeItem(child_node))
        return items
    
class AlexTreeNode(TreeNode):
    
    def selected_item(self):
    
        if self.selected:
            return self.item.node
        
        if len(self.children) == 0:
            return None
        
        for child in self.children:
            selection = child.selected_item()
            if selection:
                return selection
            
        return None
    
    def expand_recursive(self):
        self.expand(None)
        for child in self.children:
            child.expand_recursive()
        
class AlexTree(Pmw.ScrolledCanvas):  # @UndefinedVariable
    
    def __init__(self,
                 parent,
                 tree,
                 borderframe=1,
                 labelpos='n',
                 usehullsize = 1,
                 hull_width = 400,
                 hull_height = 300,
                 **kw):
        super().__init__(
                 parent,
                 borderframe=1,
                 labelpos='n',
                 usehullsize = 1,
                 hull_width = 400,
                 hull_height = 300,
                 **kw)

        self.tree = tree
        self.canvas = self.component('canvas')
        self.tree_root = None
        self.redraw_tree()
              

    def redraw_tree(self):
        self.canvas.delete('all')
        self.tree_root = AlexTreeNode(self.canvas, None, AlexTreeItem(self.tree.root_node))
        self.tree_root.update()
        self.tree_root.expand()

    def apply_filter(self, filter_string):
        visible_nodes = self.tree.apply_filter(filter_string)
        self.redraw_tree()
        return visible_nodes
        
    def expand_all(self):
        self.tree_root.expand_recursive()
        
    def clear_filter(self):
        self.tree.clear_filter()
        self.redraw_tree()

    def get(self):
        return self.selected

    def _get_selected(self):
        return self.tree_root.selected_item()

    selected = property(_get_selected)

if __name__ == "__main__":

    from tkinter import Tk
    
    class DateEntryTest:
        '''
        Testclass
        '''

        def __init__(self):
            self.root = Tk()

            self.date_entry = DateEntryFrame(self.root)
            self.date_entry.pack()
            button_frame = Frame(self.root)
            button_frame.pack()

            read = Button(button_frame, text="Read values", command=self.read_values)
            read.pack(side=LEFT)
            write = Button(button_frame, text="Set values", command=self.set_values)
            write.pack(side=LEFT)
            cancel = Button(button_frame, text="Cancel", command=self.root.quit)
            cancel.pack(side=LEFT)
        
        def set_values(self):
            '''
            Callback for setting values programmatically.
            '''
            self.date_entry.day = 1
            self.date_entry.month = 5
            self.date_entry.year = 1917

        def read_values(self):
            '''
            Fetches the entred values and displays them in a dialog.
            '''
            # pylint: disable=no-member
            result = "%s.%s.%s" % (self.date_entry.day, self.date_entry.month, self.date_entry.year)
            dialog = Pmw.MessageDialog(self.root,  # @UndefinedVariable
                                       title = 'Result',
                                       defaultbutton = 0,
                                       message_text = result)
            dialog.activate()

        def run(self):
            '''
            Runs the test.
            '''
            self.root.mainloop()
            
    DateEntryTest().run()
