'''
Created on 24.11.2016

@author: michael
'''
import unittest
from tkgui.PluginManager import PluginManager, DocumentMenuAddition
from injector import Module

class DummyModule(Module):
    
    def configure(self):
        pass
    
class DummyMenuAddition(DocumentMenuAddition):
    
    def attach_to_window(self, parent_window):
        pass
    
class DummyMenuAddition2(DocumentMenuAddition):
    
    def attach_to_window(self, parent_window):
        pass
    

class Test(unittest.TestCase):

    def setUp(self):
        
        class Config:
            
            def __init__(self):
                self.additional_modules = ("PluginManagerTest",)
                
        self.plugin_manager = PluginManager(Config())

    def testPluginManager(self):
        
        modules = self.plugin_manager.get_plugin_modules()
        
        self.assertEqual(2, len(modules))
        self.assertEqual("DummyModule", modules[0].__name__)
        self.assertEqual("DynamicModule", modules[1].__class__.__name__)

    def testCodeCreation(self):
        
        self.plugin_manager.additions = {self.plugin_manager.extension_types[0]: (DummyMenuAddition, DummyMenuAddition2)}
        module_code = self.plugin_manager._create_module_code()
        #print(module_code)
        self.assertEqual("""from injector import Key, ClassProvider, singleton, provides, inject

from PluginManagerTest import *
DOCUMENT_MENU_ADDITION1_KEY = Key("document_menu_addition1")
DOCUMENT_MENU_ADDITION2_KEY = Key("document_menu_addition2")

class DynamicModule(Module):

    def configure(self, binder):
        binder.bind(DOCUMENT_MENU_ADDITION1_KEY, ClassProvider(DummyMenuAddition), scope=singleton)
        binder.bind(DOCUMENT_MENU_ADDITION2_KEY, ClassProvider(DummyMenuAddition2), scope=singleton)


    @provides(guiinjectorkeys.DOCUMENT_MENU_ADDITIONS_KEY, scope=singleton)
    @inject(arg1=DOCUMENT_MENU_ADDITION1_KEY, arg2=DOCUMENT_MENU_ADDITION2_KEY)
    def get_document_menu_additions(self, arg1, arg2):
        return [arg1, arg2, ]
""", module_code)

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()