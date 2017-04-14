'''
Created on 24.11.2016

@author: michael
'''
import importlib
import inspect
from injector import Module

from tkgui import guiinjectorkeys  # @UnusedImport

class DocumentMenuAddition:
    '''
    This is an empty mixin class to distinguish document menu additions
    from event menu additions
    '''
    pass

class EventMenuAddition:
    '''
    This is an empty mixin class to distinguish event menu additions
    from document menu additions
    '''
    pass

class DocumentReferenceFactory:
    '''
    This is an empty mixin class to distinguish document references
    from event references
    '''
    pass

class EventReferenceFactory:
    '''
    This is an empty mixin class to distinguish event references
    from document references
    '''
    pass

class ExtensionType:
    
    def __init__(self, extension_name, injector_key, mixin_class):
        
        self.extension_name = extension_name
        self.injector_key = injector_key
        self.mixin_class = mixin_class

class PluginManager(object):
    '''
    This is an ugly beast of a class - it dynamically creates code to
    provide working dependency injection for plugins.
    
    It scans the plugin python modules for injector module classes. This
    is the easy part. Then it scans the python modules for certain
    class types that provide hooks for certain types of alexandria
    extensions and dynamically creates an injector module that binds
    this classes and generates provider methods for the found classes.
    
    Although this is not very good maintainable and debuggable code
    it simplifies plugin creation amd insertion so considerably that it
    is worth the tradeoff (at least now it seams so).
    '''

    DOCUMENT_MENU_ADDITION = 'DOCUMENT_MENU_ADDITION'
    EVENT_MENU_ADDITION = 'EVENT_MENU_ADDITION'
    DOCUMENT_REFERENCES = 'DOCUMENT_REFERENCES'
    EVENT_REFERENCES = 'EVENT_REFERENCES'

    def __init__(self, config):
        '''
        Basically reads the config for additional modules to incorporate.
        '''
        self.plugin_names = config.additional_modules
        self.extension_types = [ExtensionType(self.DOCUMENT_MENU_ADDITION,
                                              'guiinjectorkeys.DOCUMENT_MENU_ADDITIONS_KEY',
                                              DocumentMenuAddition),
                                ExtensionType(self.EVENT_MENU_ADDITION,
                                              'guiinjectorkeys.EVENT_MENU_ADDITIONS_KEY',
                                              EventMenuAddition),
                                ExtensionType(self.DOCUMENT_REFERENCES,
                                              'guiinjectorkeys.DOCUMENT_WINDOW_ADDITIONAL_REFERENCES_KEY',
                                              DocumentReferenceFactory),
                                ExtensionType(self.EVENT_REFERENCES,
                                              'guiinjectorkeys.EVENT_WINDOW_ADDITIONAL_REFERENCES_KEY',
                                              EventReferenceFactory),
                                ]
        self.additions = {}
        
    def get_plugin_modules(self):
        '''
        This returns a list of modules to use for initalizing the injector.
        '''
        
        if len(self.plugin_names) == 0:
            return []
        
        module_list = self._find_classes_derived_from_type(Module)
        for extension_type in self.extension_types:
            self.additions[extension_type] = self._find_classes_derived_from_type(extension_type.mixin_class)
        
        exec(self._create_module_code(), globals())
        exec("module_list.append(DynamicModule())", globals(), locals())

        return module_list
    
    def _create_module_code(self):
        '''
        Creates code for an injector module named 'DynamicModule'. It defines
        the necessary injector keys, provides bindings for these keys and then
        writes provider methods for the plugins.
        '''
        
        # Imports
        
        module_code = 'from injector import Key, ClassProvider, singleton, provides, inject\n\n'
        for plugin in self.plugin_names:
            module_code += 'from %s import *\n' % plugin
            
        # Keys
        for extension_type, additions in self.additions.items():
            for i in range(1, len(additions)+1):
                module_code += '%s%d_KEY = Key("%s%d")\n' % (extension_type.extension_name,
                                                             i,
                                                             extension_type.extension_name.lower(),
                                                             i)
            
        # Module
        module_code += "\nclass DynamicModule(Module):\n\n"
        # Bindings
        module_code += '    def configure(self, binder):\n'
        
        bindings = 0    
        for extension_type, additions in self.additions.items():
            for i in range(1, len(additions)+1):
                bindings += 1
                module_code += '        binder.bind(%s%d_KEY, ClassProvider(%s), scope=singleton)\n' % (
                    extension_type.extension_name,
                    i,
                    additions[i-1].__name__)
        if bindings == 0:
            module_code += '        pass\n'
        
        for extension_type, additions in self.additions.items():
            module_code += self._create_additions_provider(extension_type, additions)
            
        return module_code
    
    def _create_additions_provider(self, extension_type, additions):
        '''
        Creates a provider method for the additions of a certain type.
        The default configuration should already have a provider for
        this type that now will be overridden to actually provide the
        types found in the plugin modules.
        '''
        if len(additions) == 0:
            return ""
        
        module_code = "\n\n    @provides(%s, scope=singleton)\n" % extension_type.injector_key
        module_code += "    @inject("
        prefix = ''
        for i in range(1, len(additions)+1):
            module_code += '%sarg%d=%s%d_KEY' % (prefix, i, extension_type.extension_name, i)
            prefix = ', '
        module_code += ")\n    def get_%ss(self" % extension_type.extension_name.lower()
        for i in range(1, len(additions)+1):
            module_code += ', arg%d' % i
        module_code += "):\n        return ["
        for i in range(1, len(additions)+1):
            module_code += 'arg%d, ' % i
        module_code += "]\n"
        return module_code
        
    def _find_classes_derived_from_type(self, class_type):
        
        def sub_class_predicate(member):
            return (inspect.isclass(member) and 
                    member != class_type and # Sort out the class imports themselves
                    issubclass(member, class_type))
 
        return self._find_classes(sub_class_predicate)
        
    def _find_classes(self, predicate):
        
        classes = []
        for plugin_name in self.plugin_names:
            python_module = importlib.import_module(plugin_name)
            for member_name, member in inspect.getmembers(python_module, predicate):
                classes.append(member)
 
        return classes
