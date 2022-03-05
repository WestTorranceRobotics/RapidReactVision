import cv2 as cv
import numpy as np
import math

vid = cv.VideoCapture(1)

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
                else:
                    if biggestBallData == None or area > biggestBallData[2]:
                        biggestBallData = [center, radius, area]

    
    if biggest:
        try:
            print(biggestBallData)
            cv.circle(frame, biggestBallData[0], biggestBallData[1], color, 3)
        except:
            pass


redValues = [174, 152, 21, 6, 255, 255]
blueValues = [95, 138, 91, 119, 255, 192]

while cv.waitKey(20) != ord("q"):
    ret, frame = vid.read()
    retCopy, frameCopy = vid.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    redMask = Threshold(hsv, redValues)
    blueMask = Threshold(hsv, blueValues)

    FindBall(frame, redMask, areaThreshold=200, color=(0,0,255))
    FindBall(frame, blueMask, areaThreshold=200, color=(255,0,0))

    FindBall(frameCopy, redMask, areaThreshold=200, color=(0,0,255), biggest=True)
    FindBall(frameCopy, blueMask, areaThreshold=200, color=(255,0,0), biggest=True)

    cv.imshow("All Balls", frame)
    cv.imshow("Biggest Ball", frameCopy)

vid.release()
cv.destroyAllWindows()