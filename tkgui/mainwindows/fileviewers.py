'''
Created on 16.04.2016

@author: michael
'''
import Pmw
from tkinter import messagebox, Toplevel, Frame
from tkinter.constants import LEFT, VERTICAL, NW, BOTH, YES
from PIL.ImageTk import PhotoImage
from PIL import Image
import os

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
    
    def __init__(self):
        self.factor = 0.0
        self.photo_image = None
        
        self.window = Toplevel()
        self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)

        self.display_frame = Frame(self.window)
        self.display_frame.pack(side=LEFT)
        self.button_frame = Frame(self.window)
        self.button_frame.pack(side=LEFT)
        self.buttonbox = Pmw.ButtonBox(self.button_frame,  # @UndefinedVariable
                                       orient=VERTICAL,
                                       pady=0,
                                       padx=0)
        self.buttonbox.pack(anchor=NW)
        self.buttonbox.add('Zoom 15%', command=lambda f=self.Zoom, p=15: f(p))
        self.buttonbox.add('Zoom -15%', command=lambda f=self.Zoom, p=-15: f(p))
        self.buttonbox.add('Zoom 50%', command=lambda f=self.Zoom, p=50: f(p))
        self.buttonbox.add('Zoom -50%', command=lambda f=self.Zoom, p=-50: f(p))
        self.buttonbox.add('Quit', command=self.window.withdraw)
        self.canvas = None
        self.window.withdraw()

    def showFile(self, file, file_info):

        self.LoadImage(file, file_info.resolution)

        if self.canvas:
            self.canvas.destroy()
            
        self.canvas = Pmw.ScrolledCanvas(self.display_frame, usehullsize=1,  # @UndefinedVariable
                                     hull_width=500,
                                     hull_height=500)
        self.img_canvas = self.canvas.component('canvas')
        self.img_canvas.create_image(1,1, image=self.photo_image, anchor=NW)
        self.canvas.pack(fill=BOTH, expand=YES)
        self.canvas.resizescrollregion()
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
        self.img_canvas.delete(self.photo_image)
        self.photo_image = PhotoImage(tmpimg)
        self.img_canvas.create_image(1,1, image=self.photo_image, anchor=NW)
        self.canvas.resizescrollregion()
    
    def Quit(self):
        self.window.destroy()
        
class ExternalViewer(object):
    '''
    This calls an external programm with the file as
    first parameter
    '''
    
    def __init__(self, external_programm):
        self.external_programm = external_programm
        self.basename = os.path.basename(external_programm)

    def showFile(self, file, file_info=None):
        if os.access(self.external_programm, os.X_OK):
            os.spawnl(os.P_NOWAIT, 
                      self.external_programm, 
                      self.basename, 
                      file)
        else:
            text = _('The external viewer {} is not accessible.')\
                .format(self.external_programm)
            dialog = Pmw.MessageDialog(  # @UndefinedVariable
                None,
                title = _("Not accessible"),
                defaultbutton = 0,
                message_text = text
                )
            dialog.activate()

