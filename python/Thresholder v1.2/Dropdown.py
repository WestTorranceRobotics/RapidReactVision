from tkinter import *

class Dropdown:
    def __init__(self, master, text="Dropdown", options=["Option 1", "Option 2", "Option 3"], defualtValue=None, command=None, bg="white"):
        self.master = master
        self.dropdownCanvas = Frame(self.master, bg=bg)
        self.label = Label(self.dropdownCanvas, text=text, bg=bg)
        self.label.grid(row=0, column=0)

        self.options = options
        self.currentValue = StringVar(self.dropdownCanvas)
        if defualtValue == None:
            self.currentValue.set(options[0])
        else:
            self.currentValue.set(defualtValue)
        self.optionMenu = OptionMenu(self.dropdownCanvas, self.currentValue, *self.options, command=command)
        self.optionMenu.grid(row=0, column=1)
    
    def pack(self):
        self.dropdownCanvas.pack()
    
    def grid(self, row=0, column=0, columnspan=1):
        self.dropdownCanvas.grid(row=row, column=column, columnspan=columnspan, padx=0, pady=0)

    def place(self, relx=0.5, rely=0.5, anchor=CENTER):
        self.dropdownCanvas.place(relx=relx, rely=rely, anchor=anchor)

    def setOptions(self, options, defualtValue = None):
        self.options = options

        self.optionMenu.grid_forget()
        self.optionMenu = OptionMenu(self.dropdownCanvas, self.currentValue, *self.options)
        self.optionMenu.grid(row=0, column=1)
        
        if defualtValue == None:
            self.currentValue.set(options[0])
        else:
            self.currentValue.set(defualtValue)
    
    def value(self):
        return self.currentValue.get()

    def setCurrent(self, value):
        self.currentValue.set(value)

        self.optionMenu.grid_forget()
        self.optionMenu = OptionMenu(self.dropdownCanvas, self.currentValue, *self.options)
        self.optionMenu.grid(row=0, column=1)
