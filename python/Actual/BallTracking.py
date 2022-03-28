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

# global verificationThreshold, isTrackingRed, debug
isTrackingRed = False
debug = False

verificationThreshold = 6

"""
Checks if the sample of frames (10 as of now) has at least
verificationThreshold amount of frames with a ball

:return: True or False based on the verificationThreshold amount
"""
def verifyTarget(samples):
    count = 0
    for sample in range(len(samples)):
        if samples[sample] != -999:
            count += 1
    if count >= verificationThreshold:
        return True

    return False

"""
This is the thresholding range of colors in HSV

:return: a black and white image, with white pixels being
the pixels included in the range of values given by hsv
"""
def threshold(hsv, values):
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

"""
Find balls and draws a circle around each

:param frame: the raw frame from the camera
:param mask: the black and white masked image given by threshold() function
:param areaThreshold: the area of the image that a contour has to be bigger than in order 
                      to be considered a ball
:param color: the color of the circle that is drawn on the frame
:param biggest: determines whether or not to only find the biggest ball on the screen

:return: an array showing the distance of the ball from the center
of the camera. Ex:[128, -90]
"""
def findAndDrawCircleAroundBall(frame, mask, areaThreshold=200, color=(0,0,0), biggest=False):
    data = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    contours = data[1]

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
                    cv.circle(frame, center, radius, color, 2)
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
            cv.circle(frame, biggestBallData[0], biggestBallData[1], color, 2)
        except:
            pass

    distFromCenter = [-999, -999] # default value
    for center in centers:
        h,w,c = frame.shape
        xdist = center[0] - w/2
        ydist = -(center[1] - h/2)
        distFromCenter = [xdist, ydist]

    return distFromCenter

def main():
    print("Initializing ball tracking...")

    # initialize network table values
    NetworkTables.initialize(server = 'roborio-5124-frc.local')
    vision_nt = NetworkTables.getDefault().getTable('Vision')
    vision_nt.putNumber("vx", -999)
    vision_nt.putNumber("vy", -999)
    vision_nt.putBoolean("Ball Found", False)

    # starts camera server
    cs = CameraServer.getInstance()
    cs.enableLogging()

    # Gets the camera connected to the pi
    # If there is a problem with the camera not showing up,
    # it might be because the UsbCamera is initailized with the wrong path.
    # The path can be found in wpilibpi.local under whatever camera you need
    camera = UsbCamera("Microsoft", "/dev/video0") 
    server = cs.startAutomaticCapture(camera=camera)
    # camera.setResolution(320, 240)
    #https://robotpy.readthedocs.io/en/stable/vision/code.html
    # cs.getVideo() should return the same object as "cv.VideoCapture('FRC/BallsVid1.mp4')"
    capture = cs.getVideo()

    colorMaskFeed = cs.putVideo("Color Mask", 320, 240)
    trackedBallsFeed = cs.putVideo("Tracked Balls", 320, 240)
    frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

    blueValues = [60,100,0, 113,255,255]
    redValues = [0,170,140, 63,255,255]
    # lower, upper
    # [h,s,v, h,s,v]

    vision_nt.putNumber("lh", 87)
    vision_nt.putNumber("ls", 100)
    vision_nt.putNumber("lv", 20)

    vision_nt.putNumber("hh", 113)
    vision_nt.putNumber("hs", 255)
    vision_nt.putNumber("hv", 255)

    samples = []
    while True:
        blueValues = [
        vision_nt.getNumber("lh", 0),
        vision_nt.getNumber("ls", 0),
        vision_nt.getNumber("lv", 0),

        vision_nt.getNumber("hh", 0),
        vision_nt.getNumber("hs", 0),
        vision_nt.getNumber("hv", 0)
        ]
        aimbotEnabled = vision_nt.getBoolean("aimbot", True)

        ret, frame = capture.grabFrame(frame, 0.225)

        blur = cv.GaussianBlur(frame, (5,5), cv.BORDER_DEFAULT)
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)

        isTrackingRed = vision_nt.getBoolean("isRed", False)

        if isTrackingRed:
            redMask = threshold(hsv, redValues)
            redDistFromCenter = findAndDrawCircleAroundBall(frame, redMask, areaThreshold=200, color=(255,255,255), biggest=True)
            colorMaskFeed.putFrame(redMask)

            vision_nt.putNumber("vx", redDistFromCenter[0])
            vision_nt.putNumber("vy", redDistFromCenter[1])
        else:
            blueMask = threshold(hsv, blueValues)
            blueDistFromCenter = findAndDrawCircleAroundBall(frame, blueMask, areaThreshold=200, color=(255,255,255), biggest=True)
            colorMaskFeed.putFrame(blueMask)

            vision_nt.putNumber("vx", blueDistFromCenter[0])
            vision_nt.putNumber("vy", blueDistFromCenter[1])

            # Add this in after verifying that tracking pid works
            # 
            # Checks a group of frames and sees if the majority have a ball
            # to prevent flickering from affecting the driving
            if len(samples) == 10:
                if verifyTarget(samples):
                    vision_nt.putBoolean("Ball Found", True)
                else:
                    vision_nt.putBoolean("Ball Found", False)
                samples = []
            else:
                samples.append(blueDistFromCenter[0])

        if debug:
            redMask = threshold(hsv, redValues)
            blueMask = threshold(hsv, blueValues)
            # combines both of the masks together
            colorMaskFeed.putFrame(cv.bitwise_or(redMask, blueMask))

        trackedBallsFeed.putFrame(frame)

        #This is the delay between frames. It is in seconds
        time.sleep(0.02)

if __name__ == "__main__":
    main()