import itertools
from pydoc import visiblename
from cscore import CameraServer
from networktables import NetworkTable, NetworkTables

import cv2 as cv
import numpy as np

global team 
team = 2496
#TODO
#   Put Camera stream to shuffleboard
#   Put vision processed stream to shuffleboard
#   Put multiple streams to shuffleboard
#   Put center of ball to NetworkTables in the form of distance from center
def createSliders():
    return

areaThreshold = 0

def main():
    NetworkTables.initialize(server = 'roborio-' + str(team) + '-frc.local')
    vision_nt = NetworkTables.getDefault().getTable('Vision')
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

    outputStream = cs.putVideo("Blue Mask", 320, 240)
    trackedBlue = cs.putVideo("Tracked Blue", 320, 240)
    frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)
    while True:
        ret, frame = capture.grabFrame(frame, 0.225)

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        #Thresholding Blue color
        #This is the thresholding range of colors in HSV
        lowerBlue = np.array([92,116,71]) # add sliders for each of the 3 values in lowerblue and higherblue
        higherBlue = np.array([113,225,255])
        blueMask = cv.inRange(hsv,lowerBlue,higherBlue)
        
        #Remove Imperfections
        opened=cv.morphologyEx(blueMask, cv.MORPH_OPEN, (7,7), iterations=4)
        closed = cv.morphologyEx(opened, cv.MORPH_CLOSE, (5,5), iterations=3)
        '''
        #Look for blue circle
        bCircles = cv.HoughCircles(closed, cv.HOUGH_GRADIENT, 2, 100, param1=70, param2=30, minRadius=10,maxRadius=100)

        bCirclesData = np.array([[]])
        try:
            print(bCircles)
            if not bCircles == None:
                bCirclesData = np.uint16(np.around(bCircles))
        except:
            bCirclesData = np.uint16(np.around(bCircles))
            print(bCircles)
            
        #Draw blue circles
        foundBlue = False
        for bCircle in bCirclesData[0, :]:
            cv.circle(frame, (bCircle[0], bCircle[1]), bCircle[2], (255,0,0), 2)
            cv.circle(frame, (bCircle[0], bCircle[1]), 2, (255,0,0), 3)
            foundBlue = True
        '''

        areaThreshold = NetworkTables.getDefault().getTable("Vision").getEntry("Area Threshold").value
        _, contours, _ = cv.findContours(closed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv.contourArea(contour)
            
            if area > areaThreshold:
                cv.drawContours(frame, contour, -1, (255,0,0), 3)
        
        #This is the delay between frames as well as for exiting the loop if the q key is pressed. It is in milliseconds
        if cv.waitKey(20) == ord('q'):
            break

        outputStream.putFrame(closed)
        trackedBlue.putFrame(frame)
        #Sends data to NetworkTables for java code to work with
        vision_nt = NetworkTables.getTable('Vision')
        vision_nt.putNumber("Area Threshold", areaThreshold)
        #vision_nt.putBoolean("Blue Found", foundBlue)
        

    capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()