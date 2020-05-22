from panorama import Stitcher
import argparse
import imutils
import cv2
import time
import numpy as np
import lib_cam_caribrate
import parser
import os

name_counter = 0


def save_image(frame):

    global name_counter

    name_counter += 1

    path = "/home/pat/HG_internship/MobileRobot/video/image_group/pic_"+str(name_counter)+".png"

    cv2.imwrite(path,frame)

    return True


cap = cv2.VideoCapture("/home/pat/HG_internship/MobileRobot/video/002_forward.mp4")

success , image = cap.read()

result = None

count = 0

list_result = []

add = 0

del_path = "/home/pat/HG_internship/MobileRobot/video/image_group/*.png"

os.system("rm "+del_path)

while success:

    if count < 100 or count > 295:
        if count > 295:
            break
        success , image = cap.read()
        print(count)

        if count > 100000000:
            count = 0

        count += 1
        continue

    print(count)

    if count in []:
        count+=1
        continue

    if type(result) == type(None):
        success , imageA = cap.read()
        imageA = lib_cam_caribrate.undistort(imageA)
        imageA = imutils.resize(imageA, width=400)
        imageA = imageA[140:190 , 50:350]
        imageA = imutils.rotate_bound(imageA, 270)

    else:
        imageA = result

    success , imageB = cap.read()

    while not success:

        success , imageB = cap.read()

        print("waiting for success")
        break

    if type(imageB) == type(None):
        continue

    imageB = lib_cam_caribrate.undistort(imageB)

    imageB = imutils.resize(imageB, width=400)

    imageB = imageB[140:190 , 50:350]

    imageB = imutils.rotate_bound(imageB, 270)

    # stitch the images together to create a panorama
    stitcher = Stitcher()

    re = stitcher.stitch([imageA, imageB] , ratio = 0.85 , reprojThresh = 5.0 , showMatches=True )

    if type(re) == type(None):
        save_image(result)
        result = None
        continue

    (result , vis) = re

    result = lib_cam_caribrate.trim(result)

    cv2.imshow("Image A", imageA)
    cv2.imshow("Image B", imageB)
    cv2.imshow("Result", result)
    cv2.imshow("Vis", vis)

    count += 1

    if cv2.waitKey(0) != ord("q"):
        
        continue

    else:

        break

    


