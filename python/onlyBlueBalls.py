from cscore import CameraServer
from networktables import NetworkTables

import cv2 as cv
import numpy as np

global team 
team = 2496
#TODO
#   Put Camera stream to shuffleboard
#   Put vision processed stream to shuffleboard
#   Put multiple streams to shuffleboard
#   Put center of ball to NetworkTables in the form of distance from center
lowerH = 0
lowerS = 0
lowerV = 0
upperH = 0
upperS = 0
upperV = 0
def configureNetworkTables():
    table = NetworkTables.getTable('HSV')
    table.putNumber("LowerH", lowerH)
    table.putNumber("LowerS", lowerS)
    table.putNumber("LowerV", lowerV)
    table.putNumber("UpperH", upperH)
    table.putNumber("UpperS", upperS)
    table.putNumber("UpperV", upperV)

def main():
    NetworkTables.initialize(server = 'roborio-' + str(team) + '-frc.local')
    vision_nt = NetworkTables.getDefault().getTable('Vision')
    configureNetworkTables()

    #Using video for tracking
    # capture = cv.VideoCapture('FRC/BallsVid1.mp4') #This will open a video file

    #Creates CameraServer
    cs = CameraServer.getInstance()
    cs.enableLogging()
    #Gets the camera connected to the pi
    camera = cs.startAutomaticCapture()
    camera.setResolution(320, 240)
    #https://robotpy.readthedocs.io/en/stable/vision/code.html
    #cs.getVideo() should return the same object as "cv.VideoCapture('FRC/BallsVid1.mp4')"
    capture = cs.getVideo()

    outputStream = cs.putVideo("Camera ACTUALLY", 320, 240)
    #capture = cv.VideoCapture(0) #This gets the webcam
    frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)
    while True:
        #Get Frame, was "capture.read()"
        ret, frame = capture.grabFrame(frame, 0.225)
        # width = int(capture.get(3))
        # height = int(capture.get(4))

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        
        #Thresholding Blue color
        #This is the thresholding range of colors in HSV
        lowerH = NetworkTables.getDefault().getTable('HSV').getEntry("LowerH").value
        lowerS = NetworkTables.getDefault().getTable('HSV').getEntry("LowerS").value
        lowerV = NetworkTables.getDefault().getTable('HSV').getEntry("LowerV").value
        upperH = NetworkTables.getDefault().getTable('HSV').getEntry("UpperH").value
        upperS = NetworkTables.getDefault().getTable('HSV').getEntry("UpperS").value
        upperV = NetworkTables.getDefault().getTable('HSV').getEntry("UpperV").value
        lowerBlue = np.array([lowerH,lowerS,lowerV]) # add sliders for each of the 3 values in lowerblue and higherblue
        higherBlue = np.array([upperH,upperS,upperV])
        blueMask = cv.inRange(hsv,lowerBlue,higherBlue)
        blueLayer = cv.bitwise_and(frame, frame, mask = blueMask)

        #This is the delay between frames as well as for exiting the loop if the q key is pressed. It is in milliseconds
        if cv.waitKey(20) == ord('q'):
            break

        outputStream.putFrame(blueLayer)
        #Sends data to NetworkTables for java code to work with
        vision_nt = NetworkTables.getTable('Vision')
        # vision_nt.putBoolean("Blue Found", foundBlue)
        # vision_nt.putBoolean("Red Found", foundRed)

    capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()