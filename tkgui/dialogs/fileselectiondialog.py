'''
Created on 06.01.2016

@author: michael
'''
from tkinter import filedialog
from alexandriabase import baseinjectorkeys
from injector import inject

class FileSelectionDialog:
    '''
    Dialog for document file selection. Just
    a wrapper around filedialog to have a
    constant interface for dialogs
    '''
    
    @inject(config=baseinjectorkeys.CONFIG_KEY)
    def __init__(self, config):
        self.filetypes = config.filetypes + list(config.filetypealiases.keys())
        
    
    def activate(self, master=None, new=False):
        if new:
            return filedialog.asksaveasfilename(parent=master)
        else:
            return filedialog.askopenfilename(parent=master)
