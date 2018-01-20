'''
Created on 20.11.2015

@author: michael
'''
from tkgui.mainwindows.BaseWindow import BaseWindow
from tkinter import Frame
from tkinter.constants import FLAT, TOP, CENTER, WORD, NW, LEFT, DISABLED,\
    NORMAL
from tkgui.components.alexwidgets import AlexText, AlexButton, AlexRadioGroup
from injector import inject, singleton
from tkgui import guiinjectorkeys

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