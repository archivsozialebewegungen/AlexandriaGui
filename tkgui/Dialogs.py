'''
Created on 01.01.2018

@author: michael
'''

from tkinter.constants import TOP, LEFT, BOTH, W, X
from tkinter import Frame, filedialog
from tkgui.components.alexwidgets import AlexLabel, AlexButton, AlexEntry,\
    AlexRadioGroup, AlexComboBox, DateEntryFrame, AlexDateEntry, AlexListBox,\
    AlexTree, AlexCheckBox
from tkgui import guiinjectorkeys, _
from injector import inject, Module, ClassProvider, singleton
from alexandriabase import baseinjectorkeys

class AbstractInputDialog:
    '''
    A basic dialog skeleton for input dialogs. For simple
    message dialogs use the native dialogs of tkinter.

    This provides a rather simple framework for fast creating
    dialogs that return user input to the calling component.
    
    The framework works like this:
    
    - Make a subclass of this class
    - Overwrite the create_dialog method. You need to
      call the method in this superclass to provide you
      with the basic frames in the dialog window.
      Add your input stuff to the interior frame and
      your buttons to the button_frame (there are methods
      to help you for this)
    - Make a subclass of the AbstractInputDialogPresenter
    - Overwrite the init_dialog method if you need to
      put some data in the dialog
    - Create action methods in the presenter that
      are bound to the buttons in the dialog window
    - The actions that are considered to close the
      dialog must set the return_value property of
      the view. This will close the dialog window and
      return the return_value to the caller of activate
    - Inject the dialog presenter into the dialog
    - Inject the dialog into your component that wants to
      use it
    - Call the activate method in the dialog in your
      component. You need to set a callback for your
      value. This callback will be executed with a value
      when the presenter closes the dialog window
    '''
    
    def __init__(self, window_manager, presenter):
        self.window_manager = window_manager
        self.presenter = presenter
        self.window = None
        self.callback = None
        
    def create_dialog(self):
        '''
        Extend this method in your child class. It already
        provides three frames: interior, buttons_frame and
        errormessage. The errormessage frame already has
        a label that may be read and set by the errormessage
        property.
        To set default buttons in the button_frame, use the
        set default buttons.
        Other buttons may be set through the add_button method.
        '''

        self.window = self.window_manager.create_new_window()
        self.window.protocol("WM_DELETE_WINDOW",
                             lambda: self._set_return_value(None))
        self.window.transient()
        self.window.attributes('-topmost', True)
        self.window.withdraw()
        
        self.interior = Frame(self.window)
        self.interior.pack()
        
        self.buttons_frame = Frame(self.window)
        self.buttons_frame.pack()
        
        self.message_frame = Frame(self.window)
        self.message_frame.pack()
        
        self._errormessage = AlexLabel(self.message_frame)
        self._errormessage.pack(side=TOP)
        
    def add_button(self, label, callback):
        '''
        Fast setup method for buttons. Just provide
        a label and a callback and a button will be
        appended to the button_frame
        '''
        
        button = AlexButton(self.buttons_frame, command=callback)
        button.set(label)
        button.pack(side=LEFT)
        return button
        
    def set_default_buttons(self):
        '''
        This method may be used in child classes
        to set the default buttons OK and Cancel
        '''
        self.add_button(_('OK'), self.presenter.ok_action)
        self.add_button(_('Cancel'), self.presenter.cancel_action)
        
    def _get_errormessage(self):
        message = self._errormessage.get()
        if message == '':
            return None
        else:
            return message
        
    def _set_errormessage(self, message):
        if message == None:
            self._errormessage.set('')
        else:
            self._errormessage.set(message)
         
    def activate(self, callback, **kw):
        '''
        '''
        if self.window is None:
            self.create_dialog(**kw)
        
        if self.window is None:
            callback(None)
            return
        self.callback = callback
        
        self.presenter.view = self
        self.window.deiconify()
        self.window.grab_set()

    def _set_return_value(self, value):
        self.window.grab_release()
        self.window.withdraw()
        self.callback(value)

    return_value = property(None, _set_return_value)        
    errormessage = property(_get_errormessage, _set_errormessage)

class Wizard(AbstractInputDialog):
    
    def __init__(self, window_manager, presenter, number_of_pages, geometry="400x200"):
        
        super().__init__(window_manager, presenter)

        self.number_of_pages = number_of_pages
        self.geometry = geometry
        
        self.pages = []
        self.actions = []
        self.current = 0

    def _wizard_buttons(self):
        for index, frame in enumerate(self.pages):
            button_frame = Frame(frame, bd=1, bg='gray')
            button_frame.pack(side='bottom', fill='x')
            cancel_button = AlexButton(button_frame, text=_("Cancel"), width=10, command=self.presenter.cancel_action)
            cancel_button.pack(side='left', anchor='w', padx=5, pady=5)
            next_button = AlexButton(button_frame, text=_("Next >>"), width=10, command=self._next_page)
            next_button.pack(side='right', anchor='e', padx=5, pady=5)
            if index != 0:
                previous_button = AlexButton(button_frame, text=_("<< Prev"), width=10, command=self._prev_page)
                previous_button.pack(side='right', anchor='e', padx=5, pady=5)
                if index == len(self.pages) - 1:
                    next_button.set(_("Finish"))
                    next_button.configure(command=self.presenter.ok_action)

    def _next_page(self):
        if self.current == len(self.pages):
            return
        self.pages[self.current].pack_forget()
        self.current += 1
        self.actions[self.current]()
        self.pages[self.current].pack(fill='both', expand=1)

    def _prev_page(self):
        if self.current == 0:
            return        
        self.pages[self.current].pack_forget()
        self.current -= 1
        self.actions[self.current]()
        self.pages[self.current].pack(fill='both', expand=1)         

    def add_page_body(self, body):
        body.pack(side='top', fill='both', padx=6, pady=12)

    def page(self, page_num):
        try:
            page = self.pages[page_num]
        except KeyError("Invalid page: %s" % page_num):
            return 0
        return page

    def _set_return_value(self, value):
        self.pages = []
        self.actions = []
        self.current = 0
        super()._set_return_value(value)

    def create_dialog(self):
        
        super().create_dialog()
        self.window.geometry(self.geometry)
        
        for page in range(self.number_of_pages): # @UnusedVariable
            self.pages.append(Frame(self.window))
            self.actions.append(lambda: None)
        self.pages[0].pack(fill='both', expand=1)
        self._wizard_buttons()
        

class GenericStringEditDialog(AbstractInputDialog):
    
    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.GENERIC_INPUT_DIALOG_PRESENTER):
        super().__init__(window_manager, presenter)
    
    def create_dialog(self, 
                     label=_('Please edit string:'),
                     initvalue = ''):
        super().create_dialog()
        self.set_default_buttons()
        
        AlexLabel(self.interior, text=label).pack()
        self.entry = AlexEntry(self.interior)
        self.entry.set(initvalue)
        self.entry.pack()
        
    def _get_entry(self):
        return self.entry.get()
        
    input = property(_get_entry)
        
class GenericStringSelectionDialog(AbstractInputDialog):
    
    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.GENERIC_INPUT_DIALOG_PRESENTER):
        super().__init__(window_manager, presenter)

    def create_dialog(self, 
                     label=_('Please select:'),
                     choices = []):
        super().create_dialog()
        self.set_default_buttons()
        self.choices = choices
        self.entry = AlexRadioGroup(self.interior, 
                                    choices=self.choices, 
                                    title=label)
        self.entry.pack()

    def _get_selected_value(self):
        return self.entry.get()

    input = property(_get_selected_value)
        
class GenericBooleanSelectionDialog(AbstractInputDialog):

    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.GENERIC_INPUT_DIALOG_PRESENTER):
        super().__init__(window_manager, presenter)

    def create_dialog(self, 
                      question=_('Select yes or no')):
        super().create_dialog()
        self.add_button(_('Yes'), self.presenter.yes_action)
        self.add_button(_('No'), self.presenter.no_action)
        label = AlexLabel(self.interior)
        label.set(question)
        label.pack()
        
weekdays = (_('MO'), _('TU'), _('WE'), _('TH'), _('FR'), _('SA'), _('SU'))

class YearSelectionDialog(AbstractInputDialog):
    
    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY, 
                 presenter: guiinjectorkeys.YEAR_SELECTION_DIALOG_PRESENTER_KEY):
        super().__init__(window_manager, presenter)
        self.day = None
        self.month = None
        self.day_of_week = None

    def activate(self, callback, day, month, weekday_shortcut):
        self.day = day
        self.month = month
        self.day_of_week = weekdays.index(weekday_shortcut.upper())
        super().activate(callback)

    def create_dialog(self):
        
        super().create_dialog()
        
        label = AlexLabel(self.interior)
        label.set("%s:" % _('Please select year'))
        label.pack()
        
        self.year_combo_box = AlexComboBox(self.interior)
        self.year_combo_box.pack(padx=5, pady=5)

        self.set_default_buttons()

    def _set_year_list(self, year_list):
        self.year_combo_box.set_items(year_list)
    
    year_list = property(None, _set_year_list)
    selected_year = property(lambda self: self.year_combo_box.get())

class DateSelectionDialog(AbstractInputDialog):
    '''
    Dialog class to select an AlexDate object. When entering a
    weekday instead of a year and day and month are already set
    a year selection dialog is started.
    '''

    def __init__(self, window_manager, presenter, yearselectiondialog, number_of_entries=1):
        self.date_entry = []
        self.number_of_entries = number_of_entries
        super().__init__(window_manager, presenter)
        self.yearselectiondialog = yearselectiondialog

    def create_dialog(self):
        super().create_dialog()
        for input_field in range(0, self.number_of_entries):
            date_entry = DateEntryFrame(self.interior)
            date_entry.day_entry.bind('<KeyRelease>',
                                      lambda event, i=input_field, f='day': self._on_change(event, i, f))
            date_entry.month_entry.bind('<KeyRelease>',
                                        lambda event, i=input_field, f='month': self._on_change(event, i, f))
            date_entry.year_entry.bind('<KeyRelease>',
                                       lambda event, i=input_field, f='year': self._on_change(event, i, f))
            date_entry.pack(padx=10)
            self.date_entry.append(date_entry)
        empty_label = AlexLabel(self.interior)
        empty_label.pack()
        self.set_default_buttons()

    def _on_change(self, event, index, field):
        '''
        Pops up the year selection dialog if we have a day, a month and a weekday
        '''
        self._check_for_weekday_to_year(index)
        if field == 'day':
            self._shift_focus_from_day(index)
        if field == 'month':
            self._shift_focus_from_month(index)
        if field == 'year':
            self._shift_focus_from_year(index)
    
    def _pad_two_digit_year(self, index):
        try:
            year = int(self.date_entry[index].year)
        except ValueError:
            return
        if year <= 45:
            self.date_entry[index].year = year + 2000
        if year > 45 and year < 100:
            self.date_entry[index].year = year + 1900
            
    def _shift_focus_from_day(self, index):
        try:
            day = int(self.date_entry[index].day)
        except ValueError:
            return
        if day == 0 or day > 3:
            self.date_entry[index].month_entry.focus_set()
        
    def _shift_focus_from_month(self, index):
        try:
            month = int(self.date_entry[index].month)
        except ValueError:
            return
        if month == 0 or month > 1:
            self.date_entry[index].year_entry.focus_set()

    def _shift_focus_from_year(self, index):
        if index == len(self.date_entry) - 1:
            return
        try:
            year = int(self.date_entry[index].year)
        except ValueError:
            return
        if year > 999:
            self.date_entry[index+1].day_entry.focus_set()

    def _check_for_weekday_to_year(self, index):
        # pylint: disable=unused-argument
        search_for_year = True
        try:
            day = int(self.date_entry[index].day)
            month = int(self.date_entry[index].month)
            weekday = self.date_entry[index].year
            weekdays.index(weekday.upper())
        except ValueError:
            search_for_year = False
        if search_for_year:
            self.date_entry[index].year = self.yearselectiondialog.activate(
                lambda year: self._set_year_on_entry(index, year),
                day,
                month,
                weekday)
            
    def _set_year_on_entry(self, index, year):
        self.date_entry[index].year = year
            
    def _dialog_close(self, button):
        for index in range(0, self.number_of_entries):
            self._pad_two_digit_year(index)
        super()._dialog_close(button)
        
    def _get_days(self):
        days = []
        for entry in self.date_entry:
            days.append(entry.day)
        return days
    
    def _set_days(self, days):
        for i in range(0, self.number_of_entries):
            self.date_entry[i].day = days[i]

    def _get_months(self):
        months = []
        for entry in self.date_entry:
            months.append(entry.month)
        return months

    def _set_months(self, months):
        for i in range(0, self.number_of_entries):
            self.date_entry[i].month = months[i]

    def _get_years(self):
        years = []
        for entry in self.date_entry:
            years.append(entry.year)
        return years

    def _set_years(self, years):
        for i in range(0, self.number_of_entries):
            self.date_entry[i].year = years[i]

    days = property(_get_days, _set_days)
    months = property(_get_months, _set_months)
    years = property(_get_years, _set_years)

class SimpleDateSelectionDialog(DateSelectionDialog):
    '''
    Selects a date.
    '''

    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.DATE_SELECTION_DIALOG_PRESENTER_KEY,
                 yearselectiondialog: guiinjectorkeys.YEAR_SELECTION_DIALOG_KEY):
        super().__init__(window_manager, presenter, yearselectiondialog, 1)

class EventIdSelectionDialog(DateSelectionDialog):
    '''
    Selects a date.
    '''

    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.EVENT_ID_SELECTION_DIALOG_PRESENTER_KEY,
                 yearselectiondialog: guiinjectorkeys.YEAR_SELECTION_DIALOG_KEY):
        super().__init__(window_manager, presenter, yearselectiondialog, 1)

class DateRangeSelectionDialog(DateSelectionDialog):
    '''
    Selects a date range.
    '''

    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.DATERANGE_SELECTION_DIALOG_PRESENTER_KEY,
                 yearselectiondialog: guiinjectorkeys.YEAR_SELECTION_DIALOG_KEY):
        super().__init__(window_manager, presenter, yearselectiondialog, 2)

class DocumentIdSelectionDialog(AbstractInputDialog):
    '''
    Dialog for document id selection
    '''
    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_PRESENTER_KEY):
        super().__init__(window_manager, presenter)
        self._entry_widget = None

    def create_dialog(self, default=''):
        super().create_dialog()
        self._entry_widget = AlexEntry(self.interior)
        self._entry_widget.set(default)
        self._entry_widget.pack()
        self.set_default_buttons()
        
    def activate(self, callback, default=''):
        super().activate(callback, default=default)
        
    input = property(lambda self: self._entry_widget.get(),
                     lambda self, value: self._entry_widget.set(value))
    
class EventSelectionWizard(Wizard):
    
    @inject
    def __init__(self, 
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY, 
                 presenter: guiinjectorkeys.EVENT_SELECTION_DIALOG_PRESENTER_KEY):
        
        self.selected_event = None
        self.date_entry = None
        self.default_date = None
        self._event_list = []

        super().__init__(window_manager, presenter, number_of_pages=2)
        
    def _add_all_content(self):
        self._add_date_entry_content()
        self._add_page1_content()
        
    def _add_date_entry_content(self):
        date_entry_frame = Frame(self.page(0))
        self.add_page_body(date_entry_frame)
        self.date_entry = AlexDateEntry(parent=date_entry_frame,
                                        label=_("Please enter the event date:"),
                                        labelwidth=25)
        if self.default_date is not None:
            self.date_entry.set(self.default_date)
        self.date_entry.pack(side=TOP)
    
    def _add_page1_content(self):
        event_selection_frame = Frame(self.page(1))
        self.add_page_body(event_selection_frame)
        AlexLabel(event_selection_frame, text=_("Please select an event:")).pack(side=TOP)
        self.event_list_box = AlexListBox(event_selection_frame, width=50, height=5)  # @UndefinedVariable
        self.event_list_box.pack(fill=BOTH)
            
    def _add_actions(self):
        self.actions[1] = self.presenter.update_event_list
        
    def _get_event_list(self):
        return self._event_list
    
    def _set_event_list(self, event_list):
        self._event_list = event_list
        self.event_list_box.set_items(event_list)
    
    def _get_selected_event(self):
        return self.event_list_box.get()
        
    def activate(self, callback, default_event=None, exclude_list = []):
        
        self.callback = callback
        self.presenter.exclude_list = exclude_list
        if default_event is not None:
            self.default_date = default_event.daterange.start_date
        self.create_dialog()
        self._add_all_content()
        self._add_actions()
        super().activate(callback)

    date = property(lambda self: self.date_entry.get())
    event_list = property(_get_event_list, _set_event_list)
    input = property(_get_selected_event)
    
class EventConfirmationDialog(AbstractInputDialog):
    
    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.EVENT_CONFIRMATION_PRESENTER_KEY):
        super().__init__(window_manager, presenter)
        
    def create_dialog(self, event_list=[], date=None):

        super().create_dialog()

        self.add_button(_('Create new event'), self.presenter.cancel_action)        
        AlexLabel(self.interior,
                  text=_("Events exist on %s. Please select the event you want or create a new one") % date,
                  wraplength=550,
                  font=("Helvetica", 14, "bold")).pack() 
        event_frame = Frame(self.interior)
        event_frame.pack()
        row_counter = 0
        for event in event_list:
            description = AlexLabel(event_frame, wraplength=500, justify=LEFT, text=event.description)
            description.grid(row=row_counter, column=0, sticky=W)
            def closure(event):
                return lambda: self._set_return_value(event)
            button = AlexButton(event_frame, text=_("Goto event"),
                            command=closure(event))
            button.grid(row=row_counter, column=1)
            row_counter += 1

class GenericTreeSelectionDialog(AbstractInputDialog):
    
    def __init__(self, window_manager, presenter):
        
        super().__init__(window_manager, presenter)

        self.tree_widget = None
        self.filter_is_set = False
        
    def create_dialog(self, label=_('Select a tree node')):

        super().create_dialog()
        
        self.label = label

        self.filter_entry = AlexEntry(self.interior)
        self.filter_entry.bind("<KeyRelease>", lambda event: self._apply_filter(event))
        self.filter_entry.pack(fill=X, expand=1)
        
        self.set_default_buttons()

    def _apply_filter(self, event):
        filter_string = self.filter_entry.get()
        if len(filter_string) > 2:
            visible_nodes = self.tree_widget.apply_filter(filter_string)
            if visible_nodes < 20:
                self.tree_widget.expand_all()
            self.filter_is_set = True
        else:
            if self.filter_is_set:
                self.tree_widget.clear_filter()
                self.filter_is_set = False
    
    def set_tree(self, tree):
        if self.tree_widget is not None:
            self.tree_widget.destroy()
        self.tree_widget = AlexTree(self.interior,
                                    tree,
                                    self.label)
        self.tree_widget.pack()
    
    def activate(self, callback, label):
        self.label = label
        super().activate(callback)
                
    input = property(lambda self: self.tree_widget.get())
    tree = property(None, set_tree)

class EventTypeSelectionDialog(GenericTreeSelectionDialog):
    
    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.EVENT_TYPE_SELECTION_PRESENTER_KEY):
        super().__init__(window_manager, presenter)

class GenericFilterDialog(AbstractInputDialog):
    
    def create_dialog(self):
        super().create_dialog()
        self.add_button(_("Set filter"), self.presenter.ok_action)
        self.add_button(_("Clear form"), self._clear_filter_form)
        self.add_button(_("Cancel"), self.presenter.cancel_action)
        self.search_term_entries = []
        for i in range(1, 4):
            AlexLabel(self.interior,
                      text=_("%d. search expression:" % i)).grid(row=i - 1, column=0, sticky=W)
            entry = AlexEntry(self.interior)
            entry.grid(row=i - 1, column=1, sticky=W, pady=5)
            self.search_term_entries.append(entry)

    def _clear_filter_form(self):
        for entry in self.search_term_entries:
            entry.set('')

    def _get_searchterms(self):
        searchterms = []
        for entry in self.search_term_entries:
            value = entry.get()
            if value != '':
                searchterms.append(value)
        return searchterms
    
    searchterms = property(_get_searchterms)

class DocumentFilterDialog(GenericFilterDialog):  # @UndefinedVariable

    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.DOCUMENT_FILTER_DIALOG_PRESENTER_KEY):
        super().__init__(window_manager, presenter)

    def create_dialog(self):
        super().create_dialog()
        AlexLabel(self.interior, text=_("Signature:")).grid(row=3, column=0, sticky=W)
        self.signature_entry = AlexEntry(self.interior)
        self.signature_entry.grid(row=3, column=1, sticky=W, pady=5)
                   
    def _clear_filter_form(self):
        super()._clear_filter_form()
        self.signature_entry.set('')
    
    signature = property(lambda self: self.signature_entry.get())
    
class EventFilterDialog(GenericFilterDialog):

    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.EVENT_FILTER_DIALOG_PRESENTER_KEY):
        super().__init__(window_manager, presenter)

    def create_dialog(self):
        super().create_dialog()

        self.earliest_date_entry = AlexDateEntry(self.interior, label=_("Earliest Date"))
        self.earliest_date_entry.grid(row=3, column=0, sticky=W, pady=5, columnspan=2)
        self.latest_date_entry = AlexDateEntry(self.interior, label=_("Latest Date"))
        self.latest_date_entry.grid(row=4, column=0, sticky=W, pady=5, columnspan=2)

        AlexLabel(self.interior, text=_("Only local events")
              ).grid(row=5, column=0, sticky=W, pady=5)
        self.local_only_checkbox = AlexCheckBox(self.interior)
        self.local_only_checkbox.grid(row=5, column=1, sticky=W, pady=5)

        AlexLabel(self.interior, text=_("Only unverified events")
              ).grid(row=6, column=0, sticky=W, pady=5)
        self.unverified_only_checkbox = AlexCheckBox(self.interior)
        self.unverified_only_checkbox.grid(row=6, column=1, sticky=W, pady=5)
    
    def _clear_filter_form(self):
        super()._clear_filter_form()
        self.earliest_date_entry.set(None)
        self.latest_date_entry.set(None)
        self.local_only_checkbox.set(False)
        self.unverified_only_checkbox.set(False)

    earliest_date = property(lambda self: self.earliest_date_entry.get(),
                             lambda self, value: self.earliest_date_entry.set(value))
    latest_date = property(lambda self: self.latest_date_entry.get(),
                             lambda self, value: self.latest_date_entry.set(value))
    local_only = property(lambda self: self.local_only_checkbox.get(),
                             lambda self, value: self.local_only_checkbox.set(value))
    unverified_only = property(lambda self: self.unverified_only_checkbox.get(),
                             lambda self, value: self.unverified_only_checkbox.set(value))

class LoginDialog(Frame):
    '''
    Login dialog used during setup
    '''

    @inject
    def __init__(self,
                 window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY,
                 presenter: guiinjectorkeys.LOGIN_DIALOG_PRESENTER_KEY):
        
        self.window_manager = window_manager
        self.window = None
        self.presenter = presenter
        self._return_value = None
        
    def create_dialog(self):

        self.window = self.window_manager.create_new_window()
        self.window.withdraw()
        
        super().__init__(self.window)
        self.pack()
        
        self.combobox = AlexComboBox(self)
        self.combobox.pack()
        
        buttonframe = Frame(self)
        buttonframe.pack()
        
        AlexButton(buttonframe, text=_('OK'), command=self.presenter.ok_action).pack(side=LEFT)
        AlexButton(buttonframe, text=_('Cancel'), command=self.presenter.cancel_action).pack(side=LEFT)
        

    def activate(self):
        self.create_dialog()
        self.presenter.view = self
        self.window.deiconify()
        self.window.wait_window()
        return self._return_value

    def _set_return_value(self, value):
        self._return_value = value
        self.window_manager.remove_window(self.window)
        self.window = None
        
    def _set_creators(self, creators):
        self.combobox.set_items(creators)
        
    def _get_selected_creator(self):
        return self.combobox.get()
    
    return_value = property(None, _set_return_value)
    creators = property(None, _set_creators)
    selected_creator = property(_get_selected_creator)
    
class FileSelectionDialog:
    '''
    Dialog for document file selection. Just
    a wrapper around filedialog to have a
    constant interface for dialogs
    '''
    
    @inject
    def __init__(self, config: baseinjectorkeys.CONFIG_KEY):
        self.filetypes = config.filetypes + list(config.filetypealiases.keys())
        
    
    def activate(self, callback, new=False):
        if new:
            result = filedialog.asksaveasfilename()
        else:
            result = filedialog.askopenfilename()
        callback(result)

class DialogsTkGuiModule(Module):
    '''
    Binds all existing dialogs.
    '''
    def configure(self, binder):
        binder.bind(guiinjectorkeys.EVENT_CONFIRMATION_DIALOG_KEY,
                    ClassProvider(EventConfirmationDialog))
        binder.bind(guiinjectorkeys.GENERIC_STRING_EDIT_DIALOG_KEY,
                    ClassProvider(GenericStringEditDialog))
        binder.bind(guiinjectorkeys.GENERIC_STRING_SELECTION_DIALOG_KEY,
                    ClassProvider(GenericStringSelectionDialog))
        binder.bind(guiinjectorkeys.DATE_SELECTION_DIALOG_KEY,
                    ClassProvider(SimpleDateSelectionDialog))
        binder.bind(guiinjectorkeys.EVENT_ID_SELECTION_DIALOG_KEY,
                    ClassProvider(EventIdSelectionDialog))
        binder.bind(guiinjectorkeys.DATERANGE_SELECTION_DIALOG_KEY,
                    ClassProvider(DateRangeSelectionDialog))
        binder.bind(guiinjectorkeys.YEAR_SELECTION_DIALOG_KEY,
                    ClassProvider(YearSelectionDialog))
        binder.bind(guiinjectorkeys.EVENT_SELECTION_DIALOG_KEY,
                    ClassProvider(EventSelectionWizard))
        binder.bind(guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_KEY,
                    ClassProvider(DocumentIdSelectionDialog))
        binder.bind(guiinjectorkeys.DOCUMENT_FILTER_DIALOG_KEY,
                    ClassProvider(DocumentFilterDialog), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_FILTER_DIALOG_KEY,
                    ClassProvider(EventFilterDialog), scope=singleton)
        binder.bind(guiinjectorkeys.LOGIN_DIALOG_KEY,
                    ClassProvider(LoginDialog), scope=singleton)
        binder.bind(guiinjectorkeys.FILE_SELECTION_DIALOG_KEY,
                    ClassProvider(FileSelectionDialog), scope=singleton)
        binder.bind(guiinjectorkeys.EVENT_TYPE_SELECTION_DIALOG_KEY,
                    ClassProvider(EventTypeSelectionDialog), scope=singleton)
