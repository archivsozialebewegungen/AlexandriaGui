'''
Created on 31.10.2015

@author: michael
'''
import Pmw
from tkinter import Entry, Tk, Label, Button, StringVar
from tkinter.constants import LEFT, TOP
from alexpresenters.dialogs.abstractdialogpresenter import AbstractInputDialogPresenter

class InputDialogWindow(Pmw.Dialog):  # @UndefinedVariable
    '''
    Convenience class to get a Pmw.Dialog object that
    already has the OK and Cancel button and displays
    errormessages. It is not necessary to subclass this
    object for input dialogs.
    '''
    
    def __init__(self, master, **kw):
        super().__init__(master,
                buttons=(_('OK'), _('Cancel')),
                defaultbutton=_('OK'),
                **kw)
        self._errormessage = StringVar()
        self._errormessage_label = Label(self.interior(), textvariable=self._errormessage)
        self._errormessage_label.pack(side=TOP)
        self.withdraw()
        
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
            
    errormessage = property(_get_errormessage, _set_errormessage)
        

class AbstractInputDialog:
    '''
    An abstract class that sets the framework for
    dialog classes that gather some information from
    the user. This class itself (and its child classes)
    is not a tkinter object, so it is possible to
    use dependency injection to inject the dialog into
    other components. The binding to tkinter just happens
    on activating, not before.
    '''
    def __init__(self, presenter):
        if not isinstance(presenter, AbstractInputDialogPresenter):
            # Well, a not so stupid programming language should allow this out of the box
            raise Exception("Presenter must extend AbstractInputDialogPresenter")
        self.presenter = presenter
        self.presenter.view = self
        self.return_value = None
        self.dialog = None
        
    def activate(self, master=None, *params, **kw):
        self._init_dialog(master, *params, **kw)
        if self.dialog is None:
            self._show_dialog_creation_error()
            return None
        self.dialog.configure(command=self._dialog_close)
        self.dialog.activate()
        return self.return_value
        
    def _init_dialog(self, master, *params):
        raise Exception("Override in child class!")

    def _dialog_close(self, button):
        if button != self.dialog.component('buttonbox').button(0).config()['text'][-1]:
            self.dialog.deactivate()
            self.return_value = None
            return
        self.errormessage = None
        self.presenter.assemble_return_value()
        if not self.errormessage:
            self.dialog.deactivate()
        
    def _show_dialog_creation_error(self):
        '''Overwrite if you want an errormessage when dialog creation fails.'''
        pass
        
    def _get_errormessage(self):
        return self.dialog.errormessage
    
    def _set_errormessage(self, message):
        self.dialog.errormessage = message
        
    errormessage = property(_get_errormessage, _set_errormessage)

if __name__ == '__main__':
    
    class TestInputDialog(AbstractInputDialog):
        '''
        This is a very simple dialog that just has an entry
        field. This dialog has only two properties: The entry
        property that represents the value of the entry widget
        and (implicitly) the input property which is the full
        fledged object returned by the dialog. Incidentally these
        two properties should be exactly the same, so the
        presenter just copies the one value to the other.
        '''        
        def _init_dialog(self, master):
            input_window = InputDialogWindow(master)
            self._entry_widget = Entry(input_window.interior())
            self._entry_widget.pack()
            return input_window
            
        def _get_entry(self):
            return self._entry_widget.get()
            
        entry = property(_get_entry)
        
    class TestInputPresenter(AbstractInputDialogPresenter):
        '''
        This is a very simple presenter with minimal validation
        and no data processing: It just copies the data of the
        entry field into the return_value property, which then will
        be returned by the dialog. Except when spam is entered, then
        an error will be shown.
        '''
        
        def assemble_return_value(self):
            entry_value = self.view.entry
            if entry_value.upper() == "SPAM":
                self.view.errormessage = "No spam allowed!"
            else:
                self.view.return_value = entry_value
            
    presenter = TestInputPresenter()
    dialog = TestInputDialog(presenter)
    
    
    root = Tk()
    label = Label(root, text="<Input>")
    label.pack()
    button = Button(root, text="Start dialog", command=lambda: label.configure(text=dialog.activate(root)))
    button.pack(side=LEFT)
    button = Button(root, text="Cancel", command=root.quit)
    button.pack(side=LEFT)
    root.mainloop()
    