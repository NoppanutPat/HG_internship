from panorama import Stitcher
import argparse
import imutils
import cv2
import time
import numpy as np
import lib_cam_caribrate
import parser
import os
import sys

name_counter = 0


def save_image(frame):

    global name_counter

    name_counter += 1

    path = "/home/pat/HG_internship/MobileRobot/video/image_group/pic_"+str(name_counter)+".png"

    cv2.imwrite(path,frame)

    return True

def stitch_2pic():


    cap = cv2.VideoCapture("/home/pat/HG_internship/MobileRobot/video/002_forward.mp4")

    success , image = cap.read()

    result = None

    count = 1

    list_result = []

    add = 0

    # del_path = "/home/pat/HG_internship/MobileRobot/video/image_group/*.png"

    # os.system("rm "+del_path)

    pic_list = []

    while success:

        if count < 100 or count > 305:
            if count > 330:
                # cv2.waitKey(0)
                cv2.destroyAllWindows()
                return pic_list
            success , image = cap.read()
            # print(count)

            if count > 400:
                count = 0

            count += 1
            continue

        # print(count)

        if count in []:

            count+=1
            continue

        if type(result) == type(None) or add % 2 == 0:
            if add % 2 == 0 and type(result) != type(None):
                # print("Waitng for save to array")
                # if not cv2.waitKey(0) == 't':
                pic_list.append(result)
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

        re = stitcher.stitch([imageA, imageB] , ratio = 0.5 , reprojThresh = 5.0 , showMatches=True)

        if type(re) == type(None):
            # save_image(result)
            result = None
            continue

        (result , vis) = re

        result = lib_cam_caribrate.trim(result)

        result = result[:,:len(result[0])-(add%2)-1]

        cv2.imshow("Image A", imageA)
        cv2.imshow("Image B", imageB)
        cv2.imshow("Result", result)
        

        cv2.imshow("Vis", vis)

        count += 1
        add += 1

        if cv2.waitKey(1) == ord("q"):
            
            exit()

def recursive_stitch(pic_list,ratio,reprojThresh):

    if len(pic_list) <= 30:
        return pic_list

    print("length pic_list : ",len(pic_list))

    temp_list = []

    for i in range(len(pic_list)-1):

        imageA = np.array(pic_list[i])
        imageB = np.array(pic_list[i+1])

        cv2.imshow("ImageA",imageA)
        cv2.imshow("ImageB",imageB)

        stitcher = Stitcher()

        loop = 0

        # print("ratio : ",ratio," , reprojThresh : ",reprojThresh , " , loop : ",loop)

        try:
            re = stitcher.stitch([imageA,imageB] , ratio = ratio , reprojThresh = reprojThresh , showMatches=True)

        except ValueError:
            re = stitcher.stitch([imageB,imageA] , ratio = ratio , reprojThresh = reprojThresh , showMatches=True)

        except Exception as e:
            print("Error!! : ",e)

        if type(re) == type(None):
            print("Error!")
            continue

        (result , vis) = re

        result = lib_cam_caribrate.trim(result)
        result = result[:,:len(result[0])-1]

        cv2.imshow("result",result)
        cv2.imshow("vis",vis)

        if cv2.waitKey(0) == ord('q'):
            exit()

        elif cv2.waitKey(0) == ord('c'):
            pass

        else:
            temp_list.append(result)

    pic_list = temp_list

    pic_list = recursive_stitch(pic_list , ratio + 0.002 , reprojThresh)
    return pic_list

    
if __name__ == "__main__":

    print(sys.getrecursionlimit())

    sys.setrecursionlimit(25000)

    print(sys.getrecursionlimit())

    pic_list = stitch_2pic()
    pic_list = recursive_stitch(pic_list , 0.55 , 4.0)
    if pic_list is None:
        print("Error!!")
        exit()
    for i in range(len(pic_list)):
        cv2.imshow("Pic : "+str(i),pic_list[i])
    cv2.waitKey(0)