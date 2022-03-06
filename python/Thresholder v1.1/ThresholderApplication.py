from tkinter import *
import tkinter.font as font
import cv2 as cv
from PIL import Image, ImageTk
from Dropdown import Dropdown
from Slider import Slider
import numpy as np

def GetVidSource(source):
    imageLabel.configure(text="Getting Video Feed...", image="")
    imageLabel.update()
    global vid
    if source == "Web Camera":
        vid = cv.VideoCapture(0)
    elif source == "USB 1":
        vid = cv.VideoCapture(1)
    elif source == "USB 2":
        vid = cv.VideoCapture(2)
    elif source == "USB 3":
        vid = cv.VideoCapture(3)
    else:
        print("Invalid Input")

def SelectVideoSource(value):
    global currentVideoSource, previousVideoSource, videoSourceDropdown, imageLabel
    previousVideoSource=videoSourceDropdown.value()
    if not currentVideoSource == previousVideoSource:
        currentVideoSource = previousVideoSource
        GetVidSource(value)

#region Initializing base application and widgets

#Base window
root = Tk()
root.title("Thresholding Tool")
#root.iconbitmap("ColorWheel.ico")
root.geometry("800x620")
root.resizable(width=False, height=False)

#Dividing the window into sections
#Section 1: Video Feed Selection
selectionFrame = Frame(root, width=800, height=80, bg="light grey")
selectionFrame.grid(row=0, column=0, columnspan=2)
selectionFrame.grid_propagate(False)

videoSourceOptions = ["Web Camera", "USB 1", "USB 2", "USB 3"]
videoSourceDropdown = Dropdown(selectionFrame, text="Video Source", options=videoSourceOptions, command=SelectVideoSource, bg="light grey", defualtValue="None")
videoSourceDropdown.place()
#dropdown.grid(row=0, column=0)
previousVideoSource = videoSourceDropdown.value()
currentVideoSource = previousVideoSource

#Section 2: Video Output
outputFrame = Frame(root, width=500, height=540, bg="grey")
outputFrame.grid(row=1, column=0, rowspan=2)
outputFrame.grid_propagate(False)

outputTypeFrame = Frame(outputFrame, width=500, height=40, bg="grey")
outputTypeFrame.grid(row=0, column=0)
outputTypeFrame.grid_propagate(False)

outputTypeOptions = ["Original", "Color Mask", "Color Layer"]
outputTypeDropdown = Dropdown(outputTypeFrame, text="Output Type", bg="grey", options=outputTypeOptions)
outputTypeDropdown.place(relx=0.5, rely=0.5, anchor=CENTER)

videoFrame = Frame(outputFrame, width=500, height=500, bg="grey")
videoFrame.grid(row=1, column=0)
videoFrame.grid_propagate(False)

imageLabel = Label(videoFrame, bg="grey", text="Please Select A Video Feed", font=font.Font(size = 20))
imageLabel.place(relx=0.5, rely=0.5, anchor=CENTER)
root.update()

#Section 3: Sliders
sliderFrame = Frame(root, width=300, height=460, bg="dark grey")
sliderFrame.grid(row=1, column=1)
sliderFrame.grid_propagate(False)

sliderFrame.update()

lh=0
ls=0
lv=0
uh=255
us=255
uv=255

def UpdateColorValues(slider):
    global lh,ls,lv,uh,us,uv
    if slider == "lh":
        lh=int(lhSlider.Value())
    elif slider == "ls":
        ls=int(lsSlider.Value())
    elif slider == "lv":
        lv=int(lvSlider.Value())
    elif slider == "uh":
        uh=int(uhSlider.Value())
    elif slider == "us":
        us=int(usSlider.Value())
    elif slider == "uv":
        uv=int(uvSlider.Value())
    else:
        print("Invalid Slider")


numRows = 9
for i in range(numRows):
    sliderFrame.rowconfigure(i, minsize=sliderFrame.winfo_height()/numRows)

lowerColorLabel = Label(sliderFrame, text="Lower Color", font=font.Font(family="Helvetica", size = 15), bg="dark grey")
lowerColorLabel.grid(row=0, column=0)

lhSlider = Slider(sliderFrame, command=lambda: UpdateColorValues("lh"), labelText="Lower H", labelPos="up", range=[0,180], initialValue=lh, sliderLength=225, bg="dark grey")
lhSlider.grid(row=1, column=0)

lsSlider = Slider(sliderFrame, command=lambda: UpdateColorValues("ls"), labelText="Lower S", labelPos="up", range=[0,255], initialValue=ls, sliderLength=225, bg="dark grey")
lsSlider.grid(row=2, column=0)

lvSlider = Slider(sliderFrame, command=lambda: UpdateColorValues("lv"), labelText="Lower V", labelPos="up", range=[0,255], initialValue=lv, sliderLength=225, bg="dark grey")
lvSlider.grid(row=3, column=0)

sliderFrame.rowconfigure(4, minsize=20)

upperColorLabel = Label(sliderFrame, text="Upper Color", font=font.Font(family="Helvetica", size = 15), bg="dark grey")
upperColorLabel.grid(row=5, column=0)

uhSlider = Slider(sliderFrame, command=lambda: UpdateColorValues("uh"), labelText="Upper H", labelPos="up", range=[0,180], initialValue=uh, sliderLength=225, bg="dark grey")
uhSlider.grid(row=6, column=0)

usSlider = Slider(sliderFrame, command=lambda: UpdateColorValues("us"), labelText="Upper S", labelPos="up", range=[0,255], initialValue=us, sliderLength=225, bg="dark grey")
usSlider.grid(row=7, column=0)

uvSlider = Slider(sliderFrame, command=lambda: UpdateColorValues("uv"), labelText="Upper V", labelPos="up", range=[0,255], initialValue=uv, sliderLength=225, bg="dark grey")
uvSlider.grid(row=8, column=0)

#section 4: Copy Values Button
copyValuesFrame = Frame(root, width=300, height=80, bg="dark grey")
copyValuesFrame.grid(row=2, column=1)
copyValuesFrame.grid_propagate(False)

def CopyValues():
    global lh,ls,lv,uh,us,uv
    values=f"[{lh}, {ls}, {lv}, {uh}, {us}, {uv}]"
    root.clipboard_clear()
    root.clipboard_append(values)

copyButton = Button(copyValuesFrame, text="Copy Values", command=CopyValues)
copyButton.place(relx=0.5, rely=0.5, anchor=CENTER)

root.update()
#endregion

vid=None

windowOpen = True
while windowOpen:
    root.update()
    
    #If window has been closed
    try:
        imageLabel.winfo_exists()
    except:
        break

    #If there is no video source selected
    if videoSourceDropdown.value() == "None":
        continue

    #If video cannot be found
    if not vid.isOpened():
        imageLabel.configure(text="No Video Feed Found", image="")
        continue

    #Get image and image data
    ret, imageFrame = vid.read()
    if not ret:
        imageLabel.configure(text="No Video Feed Found", image="")
        vid.release()
        continue
    height, width, c = imageFrame.shape

    #resize image
    resizeFactor = 500/max(height, width)
    resized = cv.resize(imageFrame, (int(width*resizeFactor), int(height*resizeFactor)), interpolation=cv.INTER_AREA)

    #Convert To HSV
    hsv = cv.cvtColor(resized, cv.COLOR_BGR2HSV)

    #Threshold image
    if lh < uh:
        lowerColor = np.array([lh,ls,lv])
        upperColor = np.array([uh,us,uv])
        colorMask = cv.inRange(resized, lowerColor, upperColor)
    else:
        lowerColor = np.array([0,ls,lv])
        upperColor = np.array([uh,us,uv])
        mask1 = cv.inRange(resized, lowerColor, upperColor)

        lowerColor = np.array([lh,ls,lv])
        upperColor = np.array([180,us,uv])
        mask2 = cv.inRange(resized, lowerColor, upperColor)

        colorMask = cv.bitwise_or(mask1, mask2)
    colorLayer = cv.bitwise_and(resized, resized, mask=colorMask)

    try:
        if outputTypeDropdown.value() == "Original":
            tkFrame = ImageTk.PhotoImage(image=Image.fromarray(cv.cvtColor(resized, cv.COLOR_BGR2RGB)))
        elif outputTypeDropdown.value() == "Color Mask":
            tkFrame = ImageTk.PhotoImage(image=Image.fromarray(colorMask))
        elif outputTypeDropdown.value() == "Color Layer":
            tkFrame = ImageTk.PhotoImage(image=Image.fromarray(cv.cvtColor(colorLayer, cv.COLOR_BGR2RGB)))
    except:
        continue
    
    imageLabel.configure(image=tkFrame)

if vid != None:
    vid.release()