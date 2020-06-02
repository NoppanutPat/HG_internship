import cv2
import lib_cam_caribrate
import imutils
import numpy as np


cap = cv2.VideoCapture("/home/pat/HG_internship/MobileRobot/video/002_forward.mp4")

result = np.array([])

count = 0

result = None

while True:

    if count > 450:
        break
    
    count+=1

    success , image = cap.read()
    
    if not success:
        continue
    
    image = lib_cam_caribrate.undistort(image)
    image = imutils.resize(image, width=400)
    image = image[150:151 , 50:350]
    image = imutils.rotate_bound(image, 270)

    # print(len(image))

    if result is None:

        result = image

    else:

        print(len(image))
        print(len(result))

        result = np.concatenate((result,image),axis=1)

    cv2.imshow("image",image)
    cv2.waitKey(1)

print(result.shape[:2])

cv2.imshow("result",result)

cv2.imwrite("/home/pat/HG_internship/MobileRobot/Image/result_one_pix_stitch.png",result)

cv2.waitKey(0)

