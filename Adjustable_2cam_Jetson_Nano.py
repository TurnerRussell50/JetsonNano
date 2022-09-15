# This is a python program to control 2 IMX219 cameras on the NVIDIA Jetson Nano using some sliders
# there is also some commented-out sections that enable other features (color-tracking, etc)
# Note this program uses 3 packages: cv2, numpy, servokit

import cv2
print(cv2.__version__)
import numpy as np
from adafruit_servokit import ServoKit
kit=ServoKit(channels=16)

def nothing(x):
    pass

#This creates some sliders and gives them some default values
cv2.namedWindow('Trackbars')
cv2.moveWindow('Trackbars',1320,0)

cv2.createTrackbar('hueLower', 'Trackbars',50,179,nothing)
cv2.createTrackbar('hueUpper', 'Trackbars',100,179,nothing)

cv2.createTrackbar('hue2Lower', 'Trackbars',50,179,nothing)
cv2.createTrackbar('hue2Upper', 'Trackbars',100,179,nothing)

cv2.createTrackbar('satLow', 'Trackbars',100,255,nothing)
cv2.createTrackbar('satHigh', 'Trackbars',255,255,nothing)
cv2.createTrackbar('valLow','Trackbars',100,255,nothing)
cv2.createTrackbar('valHigh','Trackbars',255,255,nothing)

cv2.createTrackbar('Pan1','Trackbars',90,180,nothing)
cv2.createTrackbar('Tilt1','Trackbars',90,180,nothing)

cv2.createTrackbar('Pan2','Trackbars',90,180,nothing)
cv2.createTrackbar('Tilt2','Trackbars',90,180,nothing)

#This sets the display sizing and orientation
dispW=640
dispH=480
flip=2

#These are the initialization settings for cameras and their functions call assignments
cam1Set='nvarguscamerasrc sensor_id=0 !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'

cam1=cv2.VideoCapture(cam1Set)

cam2Set='nvarguscamerasrc sensor_id=1 !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'

cam2=cv2.VideoCapture(cam2Set)

#These aren't used here, but are useful for making masks based on the source size
#width=cam.get(cv2.CAP_PROP_FRAME_WIDTH)
#height=cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
#print('width:',width,'hieght:',height)


# This section does most of the real work...here we return the videos as frames, display those frames as windows, convert the Blue-Green-Red defaut format of CV2 to HSV format
# Assign their values to functions, Set the upper and lowers bound for the pan/tilt trackbars, create a 'mask' filter to select specified colors, draw bounding box around selection
# Move the servos according to pan/tilt slider's value(s), exit program with 'q'
# *Note* moving the servos to track a color selection would be ver simple, just modify the variable to adjust based on the selected mask's value(s)
while True:
    ret, frame1 = cam1.read()
    cv2.imshow('nanoCam',frame1)
    cv2.moveWindow('nanoCam',0,0)

    ret, frame2=cam2.read()
    cv2.imshow('piCam2',frame2)
    cv2.moveWindow('piCam2',640,480)
    
    hsv=cv2.cvtColor(frame1,cv2.COLOR_BGR2HSV)

    hueLow=cv2.getTrackbarPos('hueLower', 'Trackbars')
    hueUp=cv2.getTrackbarPos('hueUpper', 'Trackbars')

    hue2Low=cv2.getTrackbarPos('hue2Lower', 'Trackbars')
    hue2Up=cv2.getTrackbarPos('hue2Upper', 'Trackbars')

    Ls=cv2.getTrackbarPos('satLow', 'Trackbars')
    Us=cv2.getTrackbarPos('satHigh', 'Trackbars')

    Lv=cv2.getTrackbarPos('valLow', 'Trackbars')
    Uv=cv2.getTrackbarPos('valHigh', 'Trackbars')

    Pan1=cv2.getTrackbarPos('Pan1', 'Trackbars')
    Tilt1=cv2.getTrackbarPos('Tilt1', 'Trackbars')

    Pan2=cv2.getTrackbarPos('Pan2', 'Trackbars')
    Tilt2=cv2.getTrackbarPos('Tilt2', 'Trackbars')

    l_b=np.array([hueLow,Ls,Lv])
    u_b=np.array([hueUp,Us,Uv])

    l_b2=np.array([hue2Low,Ls,Lv])
    u_b2=np.array([hue2Up,Us,Uv])

    FGmask=cv2.inRange(hsv,l_b,u_b)
    FGmask2=cv2.inRange(hsv,l_b2,u_b2)
    FGmaskComp=cv2.add(FGmask,FGmask2)
    cv2.imshow('FGmaskComp',FGmaskComp)
    cv2.moveWindow('FGmaskComp',0,530)


    contours,hierarchy=cv2.findContours(FGmaskComp,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours=sorted(contours,key=lambda x:cv2.contourArea(x),reverse=True)
    for cnt in contours:
        area=cv2.contourArea(cnt)
        (x,y,w,h)=cv2.boundingRect(cnt)
        if area>=50:
            cv2.rectangle(frame1,(x,y),(x+w,y+h),(255,0,0),2)    
            #cv2.drawContours(frame,[cnt],0,(255,0,0),2)
            #cv2.drawContours(frame,contours,0,(255,0,0),2)
            objX=x+w/2
            objY=y+h/2

    


    kit.servo[0].angle=Pan1
    kit.servo[1].angle=Tilt1

    kit.servo[2].angle=Pan2
    kit.servo[3].angle=Tilt2

    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()