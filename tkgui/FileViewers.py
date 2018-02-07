'''
Created on 16.04.2016

@author: michael
'''
from tkinter import messagebox, Frame
from tkinter.constants import LEFT, NW, BOTH, YES, NE, ALL, X
from PIL.ImageTk import PhotoImage
from PIL import Image
import os
from injector import Module, inject, provider, singleton, Key, ClassProvider
from tkgui import _, guiinjectorkeys
from alexandriabase import baseinjectorkeys
from tkgui.components.alexwidgets import AlexButton, AlexScrolledCanvasFrame
from tkinter.messagebox import showinfo

DOCUMENT_DEFAULT_VIEWER_KEY = Key('document_default_viewer_key')
DOCUMENT_GRAPHICS_VIEWER_KEY = Key('document_graphics_viewer_key')
DOCUMENT_EXTERNAL_VIEWER_FACTORY_KEY = Key('document_external_viewer_factory_key')

class DefaultViewer(object):
    '''
    This is just a message, that for a certain
    filetype there is no viewer.
    '''

    def showFile(self, file, file_info):
        text = _('There is no viewer available\nfor the filetype %s.') % file_info.filetype
        messagebox.showwarning(_("No viewer"), text)

class GraphicsViewer():
    '''
    Viewer for graphic files
    '''
    @inject    
    def __init__(self, window_manager: guiinjectorkeys.WINDOW_MANAGER_KEY):
        self.factor = 0.0
        self.photo_image = None
        
        self.window = window_manager.create_new_window()
        self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)

        self.display_frame = Frame(self.window)
        self.display_frame.pack(anchor=NE, side=LEFT, fill=BOTH, expand = YES)
        self.button_frame = Frame(self.window)
        self.button_frame.pack(anchor=NW, side=LEFT)
        AlexButton(self.button_frame, text=_('Zoom 15%'), command=lambda f=self.Zoom, p=15: f(p)).pack(fill=X, expand=YES)
        AlexButton(self.button_frame, text=_('Zoom -15%'), command=lambda f=self.Zoom, p=-15: f(p)).pack(fill=X, expand=YES)
        AlexButton(self.button_frame, text=_('Zoom 50%'), command=lambda f=self.Zoom, p=50: f(p)).pack(fill=X, expand=YES)
        AlexButton(self.button_frame, text=_('Zoom -50%'), command=lambda f=self.Zoom, p=-50: f(p)).pack(fill=X, expand=YES)
        AlexButton(self.button_frame, text=_('Quit'), command=self.window.withdraw).pack(fill=X, expand=YES)
        self.canvas = None
        self.window.withdraw()

    def showFile(self, file, file_info):

        self.LoadImage(file, file_info.resolution)

        if self.canvas:
            self.canvas.destroy()
            
        self.canvas_frame = AlexScrolledCanvasFrame(self.display_frame, width=500, height=500)
        self.canvas = self.canvas_frame.canvas
        self.canvas.create_image(1,1, image=self.photo_image, anchor=NW)
        self.canvas_frame.pack(fill=BOTH, expand=YES)
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))
        self.window.deiconify()

    def LoadImage(self, file, resolution):
        if resolution:
            self.factor = 72.0 / resolution
        else:
            self.factor = 72.0 / 300.0
        self.image = Image.open(file)
        width = int(self.image.size[0] * self.factor)
        height = int(self.image.size[1] * self.factor)
        tmpimg = self.image.resize((width, height))
        self.photo_image = PhotoImage(tmpimg)

    def Zoom(self, percent=5):
        self.factor = self.factor * (100 + percent) / 100
        width = int(self.image.size[0] * self.factor)
        height = int(self.image.size[1] * self.factor)
        tmpimg = self.image.resize((width, height))
        self.canvas.delete(self.photo_image)
        self.photo_image = PhotoImage(tmpimg)
        self.canvas.create_image(1,1, image=self.photo_image, anchor=NW)
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))
            
    def Quit(self):
        self.window.destroy()

class ExternalViewerFactory:
    
    def get_viewer_for_program(self, external_program):
        return ExternalViewer(external_program)
        
class ExternalViewer(object):
    '''
    This calls an external programm with the file as
    first parameter
    '''
    
    def __init__(self, external_program):
        self.external_programm = external_program
        self.basename = os.path.basename(external_program)
        
    def showFile(self, file, file_info=None):
        if os.access(self.external_programm, os.X_OK):
            os.spawnl(os.P_NOWAIT, 
                      self.external_programm, 
                      self.basename, 
                      file)
        else:
            text = _('The external viewer {} is not accessible.')\
                .format(self.external_programm)
            showinfo(_('OK'), text, title=_("Not accessible"))

class DocumentViewersModule(Module):

    def configure(self, binder):
      
        binder.bind(DOCUMENT_DEFAULT_VIEWER_KEY,
                    ClassProvider(DefaultViewer), scope=singleton)
        binder.bind(DOCUMENT_GRAPHICS_VIEWER_KEY,
                    ClassProvider(GraphicsViewer), scope=singleton)
        binder.bind(DOCUMENT_EXTERNAL_VIEWER_FACTORY_KEY,
                    ClassProvider(ExternalViewerFactory), scope=singleton)
    
    @inject
    @provider
    @singleton
    def get_viewers(self,
                    config: baseinjectorkeys.CONFIG_KEY,
                    default_viewer: DOCUMENT_DEFAULT_VIEWER_KEY,
                    graphics_viewer: DOCUMENT_GRAPHICS_VIEWER_KEY,
                    external_viewer_factory: DOCUMENT_EXTERNAL_VIEWER_FACTORY_KEY) -> guiinjectorkeys.DOCUMENT_FILE_VIEWERS_KEY:
        
        viewers = {}
        defined_viewers = config.filetypeviewers
        for filetype in config.filetypes:
            viewers[filetype] = default_viewer
            if filetype in defined_viewers:
                viewer = defined_viewers[filetype]
                if viewer == 'default':
                    continue
                if viewer == 'GraphicsViewer':
                    viewers[filetype] = graphics_viewer
                    continue
                viewers[filetype] = external_viewer_factory.get_viewer_for_program(viewer)
        
        return viewers
        