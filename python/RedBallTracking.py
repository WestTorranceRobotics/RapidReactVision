import itertools
from pydoc import visiblename
from cscore import CameraServer
from networktables import NetworkTable, NetworkTables

import cv2 as cv
import numpy as np
import math 

global team 
team = 2496
#TODO
#   Put Camera stream to shuffleboard
#   Put vision processed stream to shuffleboard
#   Put multiple streams to shuffleboard
#   Put center of ball to NetworkTables in the form of distance from center
def createSliders():
    return

#areaThreshold = 0

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
        lowerRed = np.array([0,170,201]) # add sliders for each of the 3 values in lowerblue and higherblue
        higherRed = np.array([63,255,255])
        redMask = cv.inRange(hsv,lowerRed,higherRed)
        
        #Remove Imperfections
        opened=cv.morphologyEx(redMask, cv.MORPH_OPEN, (7,7), iterations=4)
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

    #areaThreshold = NetworkTables.getDefault().getTable("Vision").getEntry("Area Threshold").value
        _, contours, _ = cv.findContours(closed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        for i in range(len(contours)):
            area = cv.contourArea(contours[i])

            if area > 500:
                x,y,w,h = cv.boundingRect(contours[i])
                radius = max(w,h)/2
                center = (int(x+w/2), int(y+h/2))

                closePoints = 0
                maxError = 0.3
                for point in contours[i]:
                    dist = math.hypot(point[0][0]-center[0], point[0][1]-center[1])
                    if abs((dist/radius)-1) < maxError:
                        closePoints += 1

                print(closePoints/len(contours[i]))
                if closePoints/len(contours[i]) > 0.75:
                    cv.circle(frame, center, int(radius), (30,0,0), 3)
                    vision_nt.putNumber("Xposition", center[0]) 
                    vision_nt.putNumber("yposition", center[1])
        
        #This is the delay between frames as well as for exiting the loop if the q key is pressed. It is in milliseconds
        if cv.waitKey(20) == ord('q'):
            break

        outputStream.putFrame(closed)
        trackedBlue.putFrame(frame)
        #Sends data to NetworkTables for java code to work with
        #vision_nt.putNumber("Area Threshold", areaThreshold)
        #vision_nt.putBoolean("Blue Found", foundBlue)
        

    capture.release() 
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()