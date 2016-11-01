'''
Created on 04.10.2015

Original code is from https://code.google.com/p/python-ttk/wiki/ttkWizard

'''
import tkinter

class Wizard(tkinter.Toplevel):
    
    def __init__(self, master, presenter, number_of_pages):
        self.presenter = presenter
        self.presenter.view = self
        self.pages = []
        self.actions = []
        self.current = 0
        self.master = master
        tkinter.Toplevel.__init__(self)
        self.transient(self.master)
        
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes('-topmost', True)
        for page in range(number_of_pages): # @UnusedVariable
            self.pages.append(tkinter.Frame(self))
            self.actions.append(lambda: None)
        self.pages[0].pack(fill='both', expand=1)
        self._wizard_buttons()

    def _wizard_buttons(self):
        for index, frame in enumerate(self.pages):
            button_frame = tkinter.Frame(frame, bd=1, bg='gray')
            button_frame.pack(side='bottom', fill='x')
            cancel_button = tkinter.Button(button_frame, text=_("Cancel"), width=10, command=self.close)
            cancel_button.pack(side='left', anchor='w', padx=5, pady=5)
            next_button = tkinter.Button(button_frame, text=_("Next >>"), width=10, command=self._next_page)
            next_button.pack(side='right', anchor='e', padx=5, pady=5)
            if index != 0:
                previous_button = tkinter.Button(button_frame, text=_("<< Prev"), width=10, command=self._prev_page)
                previous_button.pack(side='right', anchor='e', padx=5, pady=5)
                if index == len(self.pages) - 1:
                    next_button.configure(text=_("Finish"), command=self.presenter.close)

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

    def close(self):
        self.destroy()
        
    def start_wizard(self):
        self.wm_deiconify()
        self.wait_window(self)
    


if __name__ == "__main__":
    root = tkinter.Tk()
    
    class Presenter:
        def close(self):
            self.view.close()
            root.quit()
            
    wizard = Wizard(root, Presenter(), number_of_pages=3)
    wizard.minsize(400, 350)
    page0 = tkinter.Label(wizard.page(0), text='Page 1')
    page1 = tkinter.Label(wizard.page(1), text='Page 2')
    page2 = tkinter.Label(wizard.page(2), text='Page 3')
    wizard.add_page_body(page0)
    wizard.add_page_body(page1)
    wizard.add_page_body(page2)
    wizard.actions[1] = lambda: print("Hallo Welt!")
    root.mainloop()
