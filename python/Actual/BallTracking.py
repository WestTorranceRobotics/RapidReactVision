import itertools
import json
import time
import sys
from pydoc import visiblename

from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer
from networktables import NetworkTablesInstance, NetworkTables

import cv2 as cv
import numpy as np
import math 

global team 
team = 5124

cameraConfigs = []
cameras_list = []

#TODO
#   Put Camera stream to shuffleboard
#   Put vision processed stream to shuffleboard
#   Put multiple streams to shuffleboard
#   Put center of ball to NetworkTables in the form of distance from center
def startCamera(config):
    """Start running the camera."""
    print("Starting camera '{}' on {}".format(config.name, config.path))
    inst = CameraServer.getInstance()
    camera = UsbCamera(config.name, config.path)
    server = inst.startAutomaticCapture(camera=camera, return_server=True)

    camera.setConfigJson(json.dumps(config.config))
    camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

    if config.streamConfig is not None:
        server.setConfigJson(json.dumps(config.streamConfig))

    return camera

def Threshold(hsv, values):
    if values[0] < values[3]:
        lowerColor = np.array(values[0:3])
        upperColor = np.array(values[3:6])
        return cv.inRange(hsv, lowerColor, upperColor)
    else:
        lowerColor = np.array([0,values[1],values[2]])
        upperColor = np.array([values[3:6]])
        mask1 = cv.inRange(hsv, lowerColor, upperColor)

        lowerColor = np.array([values[0:3]])
        upperColor = np.array([180,values[4],values[5]])
        mask2 = cv.inRange(hsv, lowerColor, upperColor)

        return cv.bitwise_or(mask1, mask2)

def FindBall(frame, mask, areaThreshold=200, color=(0,0,0), biggest=False):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    biggestBallData = None #[center, radius, area]
    centers = []
    for i in range(len(contours)):
        area = cv.contourArea(contours[i])
        if area > areaThreshold:
            x,y,w,h = cv.boundingRect(contours[i])
            radius = int(max(w,h)/2)
            center = (int(x+w/2), int(y+h/2))

            closePoints = 0
            maxError = 0.25
            for point in contours[i]:
                dist = math.hypot(point[0][0]-center[0], point[0][1]-center[1])
                if abs((dist/radius)-1) < maxError:
                    closePoints += 1
            if closePoints/len(contours[i]) > 0.75:
                if not biggest:
                    cv.circle(frame, center, radius, color, 3)
                    centers.append(center)
                else:
                    if biggestBallData == None or area > biggestBallData[2]:
                        biggestBallData = [center, radius, area]
                        if len(centers) == 0:
                            centers.append(center)
                        else:
                            centers[0] = center

    
    if biggest:
        try:
            cv.circle(frame, biggestBallData[0], biggestBallData[1], color, 3)
        except:
            pass

    distFromCenter = []
    for center in centers:
        h,w,c = frame.shape
        xdist = center[0] - w/2
        ydist = -(center[1] - h/2)
        distFromCenter.append((xdist, ydist))

    return distFromCenter

def main():
    NetworkTables.initialize(server = 'roborio-' + str(team) + '-frc.local')
    vision_nt = NetworkTables.getDefault().getTable('Vision')

    #Creates CameraServer
    cs = CameraServer.getInstance()
    cs.enableLogging()
    #Gets the camera connected to the pi
    
    camera = UsbCamera("Fishtest", "/dev/video2")
    server = cs.startAutomaticCapture(camera=camera, return_server=True)
    # camera = cs.startAutomaticCapture()
    # camera.setResolution(320, 240)
    #https://robotpy.readthedocs.io/en/stable/vision/code.html
    #cs.getVideo() should return the same object as "cv.VideoCapture('FRC/BallsVid1.mp4')"
    capture = cs.getVideo()

    redBlueMask = cs.putVideo("Red and Blue Mask", 320, 240)
    trackedBalls = cs.putVideo("Tracked Balls", 320, 240)
    frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

    blueValues = [0,0,0,180,255,255]
    redValues = [0,0,0,180,255,255]
    while True:
        ret, frame = capture.grabFrame(frame, 0.225)

        blur = cv.GaussianBlur(frame, (5,5), cv.BORDER_DEFAULT)
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)

        #Thresholding Blue and Red colors
        #This is the thresholding range of colors in HSV
        blueMask = Threshold(hsv, blueValues)
        redMask = Threshold(hsv, redValues)
        
        #Returns an array showing the distances from the center Ex:[(-12,234), (128,-90)]
        #Find blue balls and draw circle around them
        blueDistFromCenter = FindBall(frame, blueMask, areaThreshold=200, color=(255,0,0))
        #Find red balls and draw circle around them
        redDistFromCenter = FindBall(frame, redMask, areaThreshold=200, color=(0,0,255))
        
        #This is the delay between frames. It is in seconds
        time.sleep(0.02)

        redBlueMask.putFrame(cv.bitwise_or(redMask, blueMask))
        trackedBalls.putFrame(frame)
        #Sends data to NetworkTables for java code to work with
        #vision_nt.putNumber("Area Threshold", areaThreshold)
        #vision_nt.putBoolean("Blue Found", foundBlue)

if __name__ == "__main__":
    main()