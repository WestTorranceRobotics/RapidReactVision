from tkinter import *
from tokenize import String

class Slider:

    def OnMoved(self, value, command=None):
        if command == None:
            pass
        else:
            command()
        self.textbox.configure(text=str(value))

    def __init__(self, master, command=None, labelText="Slider", range=[0,100], textboxWidth=5, sliderLength=300, resolution=1, labelPos="left", bg="white", initialValue=None):
        self.master = master

        self.sliderCanvas = Frame(self.master, bg=bg)

        self.label = Label(self.sliderCanvas, text=labelText, bg=bg)
        if labelPos.lower() == "up":
            self.label.grid(row=0, column=1)
        elif labelPos.lower() == "left":
            self.label.grid(row=1, column=0)
        else:
            print("Invalid Position")
            self.label.grid(row=1, column=0)

        self.textbox = Label(self.sliderCanvas, width=textboxWidth, bg=bg)
        self.textbox.grid(row=1, column=1)

        self.sliderRange = range
        self.sliderValue = DoubleVar(self.sliderCanvas)
        if initialValue == None:
            self.sliderValue.set(range[0])
        elif initialValue < range[0]:
            self.sliderValue.set(range[0])
        elif initialValue > range[1]:
            self.sliderValue.set(range[1])
        else:
            self.sliderValue.set(initialValue)

        self.previousValue = self.sliderValue.get()
        self.slider = Scale(self.sliderCanvas, variable = self.sliderValue, from_=range[0], to=range[1], orient=HORIZONTAL, length=sliderLength, showvalue=0, command=lambda value: self.OnMoved(value, command=command), sliderlength=15, resolution=resolution, bg=bg)
        self.slider.grid(row=1, column=2)

        if resolution == 1:
            self.textbox.configure(text=str(int(self.sliderValue.get())))
        else:
            self.textbox.configure(text=str(self.sliderValue.get()))
    
    def pack(self):
        self.sliderCanvas.pack()

    def grid(self, row=0, column=0, columnspan=1):
        self.sliderCanvas.grid(row=row, column=column, columnspan=columnspan)

    def Value(self):
        return self.sliderValue.get()