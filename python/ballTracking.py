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

    outputStream = cs.putVideo("Camera 1", 320, 240)
    #capture = cv.VideoCapture(0) #This gets the webcam

    while True:
        #Get Frame, was "capture.read()"
        ret, frame = capture.grabFrame()
        # width = int(capture.get(3))
        # height = int(capture.get(4))

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        
        #Thresholding Blue color
        #This is the thresholding range of colors in HSV
        lowerBlue = np.array([90,50,50])
        higherBlue = np.array([140,255,255])
        blueMask = cv.inRange(hsv,lowerBlue,higherBlue)
        blueLayer = cv.bitwise_and(frame, frame, mask = blueMask)
        
        #Look for blue circle
        blurredBlueLayer = cv.GaussianBlur(blueLayer, (7,7), cv.BORDER_CONSTANT)
        greyedBlueLayer = cv.cvtColor(blurredBlueLayer, cv.COLOR_BGR2GRAY)
        bCircles = cv.HoughCircles(greyedBlueLayer, cv.HOUGH_GRADIENT, 2, 100, param1=70, param2=30, minRadius=10,maxRadius=150)

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
        
        
        #Thresholding red color
        #This is the thresholding range of colors in HSV
        lowerRed = np.array([175,100,100])
        higherRed = np.array([200,255,255])    
        redMask = cv.inRange(hsv,lowerRed,higherRed)
        redLayer = cv.bitwise_and(frame, frame, mask = redMask)

        #Look for red circle
        blurredRedLayer = cv.GaussianBlur(redLayer, (7,7), cv.BORDER_CONSTANT)
        greyedRedLayer = cv.cvtColor(blurredRedLayer, cv.COLOR_BGR2GRAY)
        rCircles = cv.HoughCircles(greyedRedLayer, cv.HOUGH_GRADIENT, 2, 100, param1=60, param2=50, minRadius=10,maxRadius=100)

        rCirclesData = np.array([[]])
        try:
            if not rCircles == None:
                rCirclesData = np.uint16(np.around(rCircles))
        except:
            rCirclesData = np.uint16(np.around(rCircles))
            
        #Draw red circles
        foundRed = False
        for rCircle in rCirclesData[0, :]:
            cv.circle(frame, (rCircle[0], rCircle[1]), rCircle[2], (0,0,255), 2)
            cv.circle(frame, (rCircle[0], rCircle[1]), 2, (0,0,255), 3)
            foundRed = True

        #Show the frame
        # cv.imshow("Webcam", frame)

        #This is the delay between frames as well as for exiting the loop if the q key is pressed. It is in milliseconds
        if cv.waitKey(20) == ord('q'):
            break

        #Sends data to NetworkTables for java code to work with
        vision_nt = NetworkTables.getTable('Vision')
        vision_nt.putBoolean("Blue Found", foundBlue)
        vision_nt.putBoolean("Red FOund", foundRed)

    capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()