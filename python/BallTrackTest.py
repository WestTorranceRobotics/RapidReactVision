import cv2 as cv
import numpy as np
import math

vid = cv.VideoCapture(0)

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
    contours, out = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
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


redValues = [0, 143, 116, 14, 255, 255]

while cv.waitKey(20) != ord("q"):
    ret, frame = vid.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    redMask = Threshold(hsv, redValues)

    data = FindBall(frame, redMask, areaThreshold=200, color=(0,0,255))

    print(data)

    # FindBall(frameCopy, redMask, areaThreshold=200, color=(0,0,255), biggest=True)
    # FindBall(frameCopy, blueMask, areaThreshold=200, color=(255,0,0), biggest=True)

    cv.imshow("All Balls", frame)
vid.release()
cv.destroyAllWindows()