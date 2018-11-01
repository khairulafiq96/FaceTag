import numpy as np
import cv2
import fileinput

import configparser
#sudo apt-get install qt5-default libqt5webkit5-dev build-essential python-lxml python-pip xvfb
#sudo pip3 install dryscrape
config = configparser.ConfigParser()
config.read("myConfig.ini")
videoLink = config.get("myVars", "webcamLink")

# Open a sample video available in sample-videos
vcap = cv2.VideoCapture(videoLink)
#if not vcap.isOpened():
#    print "File Cannot be Opened"

while(True):
    # Capture frame-by-frame
    ret, frame = vcap.read()
    #print cap.isOpened(), ret
    def updateValue (my_status):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read("myConfig.ini")
        config.set("myVars", "webcamStatus", my_status)

        with open("myConfig.ini", 'w') as configfile:
            config.write(configfile)

    if frame is not None:
        curr_stat = "WEBCAM IS DETECTED"
        updateValue(curr_stat)
        vcap.release()
        print("Contains Webcam")
        break
    else:
        curr_stat = "NO WEBCAM IS DETECTED"
        updateValue(curr_stat)
        print ("No Webcam")
        vcap.release()
        break
