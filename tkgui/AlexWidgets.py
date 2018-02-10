'''
Created on 21.11.2015

This module mostly wraps tkinter widgets to get them a
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
    Entry, Checkbutton, Menu, PhotoImage, Canvas, Listbox, Toplevel, TclError
from tkinter import Tk
from tkinter.constants import END, DISABLED, ALL, N, S, E, W, LEFT, NORMAL,\
    HORIZONTAL, GROOVE, SUNKEN, SOLID
from alexandriabase.domain import AlexDate
from builtins import Exception
from tkinter.ttk import Combobox, Scrollbar
from tkgui import _

try:
    # Python 3.4 and Python 3.5
    from idlelib.TreeWidget import TreeItem, TreeNode
except:
    # Since Python 3.6
    from idlelib.tree import TreeItem, TreeNode  # @UnresolvedImport

class AlexTk(Tk):
    '''
    Just a wrapper class to switch between
    tkinter and tkinter.tix
    '''

class AlexWidget:
    '''
    Mixin class for adding tooltips
    '''
    def addToolTip(self, text):
        toolTip = AlexToolTip(self)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        self.bind('<Enter>', enter)
        self.bind('<Leave>', leave)

class DateEntryFrame(Frame):
    # pylint: disable=too-many-ancestors
    '''
    A simple widget just to enter dates - without any validation
    '''

    def __init__(self, parent, label=_('Date'), labelwidth=15):
        Frame.__init__(self, parent)

        self._label = AlexLabel(self, text=label, width=labelwidth)
        self._label.pack(side=LEFT)
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
    label = property(lambda self: self._label.get(),
                     lambda self, text: self._label.set(text))

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
    def __init__(self, *params, **kw):
        
        super().__init__(*params, **kw)
        self.object = None
    
    def set(self, display_object):
        '''
        Sets the string representation of the given display_object.
        '''
        self.object = display_object
        self.configure(text="%s" % display_object)
        
    def get(self):
        '''
        Returns the object.
        '''
        return self.object

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
        
class AlexButton(AlexWidget, Button):
    '''
    Wrapper around the tkinter Button class
    '''
    
    def __init__(self, *params, **kw):
        
        self.textvar = StringVar()
        self.object = None
        
        super().__init__(*params, textvariable=self.textvar, **kw)
        if 'text' in kw:
            self.set(kw['text'])
            
    def set(self, value):
        '''
        Converts the value to string, strips it of leading and
        trailing whitspaces and sets it as button value.
        The original object is preserved.
        '''
        self.object = value
        text = "%s" % value
        self.textvar.set(text.strip())
        
    def get(self):
        '''
        Returns the initial object.
        '''
        return self.object
    
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

class AlexScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        super().set(lo, hi)

class AlexListBox(Frame):
    
    def __init__(self, parent, items=[], width=20, height=10,
                 selectioncommand=None):
        
        super().__init__(parent)
        
        self.selectioncommand = selectioncommand
        
        self.listbox = Listbox(self, width=width, height=height)
        self.listbox.grid(row=0, column=0)
        scrollbar_y = AlexScrollbar(self, command=self.listbox.yview)
        scrollbar_y.grid(row=0, column=1, sticky=N+S)
        self.listbox.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_x = AlexScrollbar(self, command=self.listbox.xview,
                                orient=HORIZONTAL)
        scrollbar_x.grid(row=1, column=0, sticky=E+W)
        self.listbox.configure(xscrollcommand=scrollbar_x.set)
        if self.selectioncommand is not None:
            self.listbox.bind('<<ListboxSelect>>', self._select_callback)
        self.set_items(items)
        
    def _select_callback(self, event):
        
        selection = self.get()
        # ignore unselect
        if selection != None:
            self.selectioncommand(selection)

    def set_items(self, items):
        
        self.listbox.delete(0, END)
        self.items = []
        for item in items:
            self.items.append(item)
            self.listbox.insert(END, "%s" % item)
            
    def get_items(self):
        
        return self.items
        
        
    def get(self):
        
        selections = self.listbox.curselection()
        if len(selections) > 0:
            return self.items[selections[0]]
        else:
            return None
    
    def set(self, selection):
        
        self.listbox.selection_clear(0, len(self.items))
        for i in range(0, len(self.items)):
            if self.items[i] == selection:
                self.listbox.selection_set(i)

class AlexScrolledCanvasFrame(Frame):
    
    def __init__(self, parent, width=20, height=10):
        
        super().__init__(parent, bd=4, relief=SUNKEN)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.canvas = Canvas(self, width=width, height=height)
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
        scrollbar_y = AlexScrollbar(self, command=self.canvas.yview)
        scrollbar_y.grid(row=0, column=1, sticky=N+S)
        self.canvas.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_x = AlexScrollbar(self, command=self.canvas.xview,
                                orient=HORIZONTAL)
        scrollbar_x.grid(row=1, column=0, sticky=E+W)
        self.canvas.configure(xscrollcommand=scrollbar_x.set)
        
class AlexComboBox(Combobox):
    '''
    A Combobox subclass that supports arbitrary objects as
    items, as long as the __str__ method is implemented and
    returns a unique string for each item. This string is
    what will be displayed in the combo box.
    '''
    
    def __init__(self, parent, items=[]):
        
        self._selection = StringVar()
        super().__init__(parent,
                         state='readonly',
                         textvariable=self._selection)
        self._item_map = {}
        self.set_items(items)
        
    def set_items(self, items):
        '''
        Takes a list of items to be displayed in the combobox.
        The first element will be selected.
        '''
        
        values = []
        self._items = items
        self._item_map = {}
        for item in items:
            item_string = "%s" % item
            self._item_map[item_string] = item
            values.append(item_string)
            
        self.configure(values=values)
        if len(values) > 0:
            self._selection.set(values[0])
        else:
            self._selection.set('')
            
    def get_items(self):
        '''
        Returns all the items in the combo box (for whatever
        reason you do want this)
        '''
        return self._items
    
    def set(self, item):
        '''
        Select an item in the combo box programmatically. If
        the item is not part of the combo box, an Exception
        will be thrown.
        '''
        
        if not item in self._item_map.values():
            raise(Exception("Item %s is not in items for combo box" % item))
        self._selection.set("%s" % item)
        
    def get(self):
        '''
        Get the item that is selected in the combo box.
        '''
        if len(self._item_map) > 0:
            return self._item_map[self._selection.get()]
        else:
            return None
    

class AlexMessageBar(AlexEntry):  # @UndefinedVariable
    '''
    It displays all messages sent by the message broker that have
    the attributes 'messagetype' and 'message'. 'messagetype' may
    be error, warning, info and debug.
    It is possible to configure which alexandria messages should be
    shown using the method config_messages which expects a message key.
    If this configuration is used, only the messages configured
    will be shown.
    '''
    def __init__(self, *params, **kw):
        super().__init__(*params, **kw)
        self.current_message = None
    
    def show_message(self, message):
        self.current_message = message
        self.set(message.message)
        self.after(5000, lambda: self.clear_message(message))
    
    def clear_message(self, message):
        if message == self.current_message:
            self.set('')
            self.current_message = None
            
    def receive_message(self, message):
        if hasattr(message, 'messagetype') and hasattr(message, 'message'):
            self.show_message(message)

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
      
class AlexTree(Frame):  # @UndefinedVariable
    
    def __init__(self,
                 parent,
                 tree):
        super().__init__(
                 parent,
                 width = 400,
                 height = 300
                 )

        self.tree = tree

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        xscrollbar = AlexScrollbar(self, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=E+W)

        yscrollbar = AlexScrollbar(self)
        yscrollbar.grid(row=0, column=1, sticky=N+S)

        canvasframe = Frame(self, bd=4, relief=GROOVE)
        canvasframe.grid(row=0, column=0, sticky=N+S+E+W)
        self.canvas = Canvas(canvasframe, bd=0,
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set)
        self.canvas.pack(padx=1, pady=1)


        xscrollbar.config(command=self.canvas.xview)
        yscrollbar.config(command=self.canvas.yview)
        
        self.tree_root = None
        self.redraw_tree()
              

    def redraw_tree(self):
        self.canvas.delete(ALL)
        self.tree_root = AlexTreeNode(self.canvas, None, AlexTreeItem(self.tree.root_node))
        self.tree_root.update()
        self.tree_root.expand()
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

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

    def set(self, entity_id):
        '''
        This is quite complicated. We need to
        expand the tree recursively. This is done
        in _get_tree_item.
        '''
        self.tree_root.deselectall()
        entity = self.tree.get_by_id(entity_id)
        item = self._get_tree_item(entity)
        item.select()
        
    def _get_tree_item(self, entity):
        '''
        Recursively get the parent tree item,
        then expand it (so the children become
        searchable), search the child and
        return it.
        '''

        if entity.parent_id is None:
            # OK, our recursion has ended
            return self.tree_root
        else:
            # Still not at root. Get the parent.
            parent = self.tree.get_by_id(entity.parent_id)
            parent_node = self._get_tree_item(parent)
        
        # Now we have the parent node, so we can expand it
        # a) to show the children on the canvas and
        # b) to make the children property searchable    
        parent_node.expand()
        
        # Now we can search for the child node
        for child_node in parent_node.children:
            if child_node.item.node.id == entity.id:
                return child_node

    def _get_selected(self):
        return self.tree_root.selected_item()

    selected = property(_get_selected)

class AlexMenuBar(Menu):
    '''
    Enhances the default menu class from tkinter
    to make adding and inserting menu items more
    natural.
    '''
    
    def __init__(self, *params, **kw):
        super().__init__(*params, **kw)
        self.entries = {}
        self.menus = {}
        self.callbacks = {}
        self.shortcutindex = 0
        
    def addmenu(self, *params, **kw):

        menulabel = params[0]
        self.entries[menulabel] = []
        self.menus[menulabel] = Menu(self, tearoff=False)
        self.insert(len(self.menus), 'cascade', label=menulabel, menu=self.menus[menulabel])
                
    def addmenuitem(self, *params, before=None, **kw):
        menulabel = params[0]
        itemlabel = kw['label']
        callback = kw['command']

        menu = self.menus[menulabel]
                
        if before is None:
            menu.add(*params[1:], **kw)
            self.entries[menulabel].append(itemlabel)
        else:
            position = self._findPosition(menulabel, before)
            menu.insert(position, *params[1:], **kw)
            self.entries[menulabel].insert(position, itemlabel)

        self.callbacks['%s-%s' % (menulabel, itemlabel)] = callback

    def hasmenu(self, menulabel):
        
        return menulabel in self.menus
    
    def get_callback(self, menulabel, itemlabel):
        
        return self.callbacks['%s-%s' % (menulabel, itemlabel)]
    
    def _findPosition(self, menuName, before):
        
        counter = 0
        for entry in self.entries[menuName]:
            if entry == before:
                return counter
            counter += 1
            
        return counter

class AlexShortcutBar(Frame):
    
    def __init__(self, *p, **kw):
        super().__init__(*p, **kw)
        self.images = []
    
    def addshortcut(self, imagefile='', command='', tooltip=None):
        

        self.images.append(PhotoImage(master=self, file=imagefile))
        button = AlexButton(self, image=self.images[-1], command=command)
        if tooltip is not None:
            button.addToolTip(tooltip)
        button.pack(side=LEFT)    
        
class AlexToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")  # @UnusedVariable
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

