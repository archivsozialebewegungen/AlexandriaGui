'''
Created on 06.01.2016

@author: michael
'''
from tkgui.dialogs.abstractdialog import AbstractInputDialog, InputDialogWindow
from tkgui.components.alexwidgets import AlexEntry, AlexLabel
from tkinter import Tk, Button
from alexpresenters.dialogs.documentid_selection_dialog_presenter \
    import DocumentIdSelectionDialogPresenter
from tkinter.constants import LEFT, TOP
from injector import inject
from tkgui import guiinjectorkeys

class DocumentIdSelectionDialog(AbstractInputDialog):
    '''
    Dialog for document id selection
    '''
    @inject(presenter=guiinjectorkeys.DOCUMENTID_SELECTION_DIALOG_PRESENTER_KEY)
    def __init__(self, presenter):
        super().__init__(presenter)
        self._entry_widget = None

    def _init_dialog(self, master, *params):
        self.dialog = InputDialogWindow(master)
        self._entry_widget = AlexEntry(self.dialog.interior())
        if len(params) == 1:
            self._entry_widget.set(params[0])
        self._entry_widget.pack()
        
    input = property(lambda self: self._entry_widget.get(),
                     lambda self, value: self._entry_widget.set(value))
    
if __name__=='__main__':

    class DocumentIdSelectionTest():
        '''
        Manual test for date selection and date range selection
        '''
        def __init__(self):
            self.root = Tk()

            label = AlexLabel(self.root)
            label.pack(side=TOP)

            documentid_dialog = DocumentIdSelectionDialog(
                DocumentIdSelectionDialogPresenter())

            button = Button(
                self.root,
                text="Start document id selection dialog",
                command=lambda: label.set(documentid_dialog.activate(self.root)))
            button.pack(side=LEFT)

            button = Button(
                self.root,
                text="Cancel",
                command=self.root.quit)
            button.pack(side=LEFT)

        def run(self):
            '''Runs the test'''

            self.root.mainloop()

    DocumentIdSelectionTest().run()
