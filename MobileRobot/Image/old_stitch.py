from panorama import Stitcher
import cv2
import lib_cam_caribrate
import imutils
import numpy as np
import time
import sys

cap = cv2.VideoCapture("/home/pat/HG_internship/MobileRobot/video/002_forward.mp4")

count = 0

image_list = []

toolbar_width = 10

stitch = Stitcher()

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

while True:

    success , image = cap.read()

    if not success:

        continue

    if count < 50 or count > 365:
        if count > 350:
            break
        success , image = cap.read()
        # print(count)

        if count > 100000000:
            count = 0

        count += 1
        continue

    if count % 2 != 0:

        count+=1
        continue

    # print(count)
    image = lib_cam_caribrate.undistort(image)
    image = imutils.resize(image, width=400)
    image = image[140:190 , 50:350]
    image = imutils.rotate_bound(image, 270)
    image_list.append(image)

    sys.stdout.write("|")
    sys.stdout.flush()

    # cv2.imshow("image",image)

    # if cv2.waitKey(1) != ord("q"):
        
    #     pass

    # else:

    #     break

    count+=1

sys.stdout.write("]\n") # this ends the progress bar


kps_list = []
feature_list = []

for i in image_list:

    stitch.isv3 = imutils.is_cv3(or_better=True)

    (kps , feature) = stitch.detectAndDescribe(i)
    kps_list.append(kps)
    feature_list.append(feature)

M_list = []

for i in range(0,len(kps_list)-1):

    M = stitch.matchKeypoints(kps_list[i+1],kps_list[i],feature_list[i+1],feature_list[i],0.85,10.0)

    if M is None:

        print("M is None , i : ",i)

    M_list.append(M)

result = None

print(len(image_list))
print(len(kps_list))
print(len(feature_list))
print(len(M_list))

for i in range(0,len(M_list)-2):

    print("i after m : ",i)

    if M_list[i] is None:

        print("M is noneeee")

        continue

    (matches, H, status) = M_list[i]

    if i == 0:

        imageA = image_list[i+1]
        imageB = image_list[i]

    else:

        cv2.imshow("old_result",result)

        imageA = result
        imageB = image_list[i+1]

    kpsA = kps_list[i+1]
    kpsB = kps_list[i]

    print(imageA.shape[:2])
    print(imageB.shape[:2])

    try:
        result = cv2.warpPerspective(imageA, H, (imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
        cv2.imshow("result_before",result)
        result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB
    except Exception as e:
        print("Error!!",e)
        exit()

    vis = stitch.drawMatches(imageA, imageB, kpsA, kpsB, matches,status)

    result = lib_cam_caribrate.trim(result)

    print(result.shape[:2])
    print(imageB.shape[:2])

    cv2.imshow("Image A", imageA)
    cv2.imshow("Image B", imageB)
    cv2.imshow("result",result)
    cv2.imshow("vis",vis)

    if cv2.waitKey(0) == ord("q"):

        break


