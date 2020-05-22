from panorama import Stitcher
import argparse
import imutils
import cv2
import time
import numpy as np
import cam_caribrate
import parser

def trim(frame):
    #crop top
    if not np.sum(frame[0]):
        return trim(frame[1:])
    #crop bottom
    elif not np.sum(frame[-1]):
        return trim(frame[:-2])
    #crop left
    elif not np.sum(frame[:,0]):
        return trim(frame[:,1:]) 
    #crop right
    elif not np.sum(frame[:,-1]):
        return trim(frame[:,:-2])    
    return frame

parser = argparse.ArgumentParser(description='Stitch')

parser.add_argument('--file', type=str, required=False, help='YML file to load calibration matrices')

args = parser.parse_args()

mtx , dist = cam_caribrate.load_coefficients(args.file)

cap = cv2.VideoCapture("/home/pat/HG_internship/MobileRobot/video/002_forward.mp4")

success , image = cap.read()

result = "as"

count = 0

list_result = []

add = 0

while success:

    if count < 100:
        success , image = cap.read()
        print(count)

        if count > 100000000:
            count = 0

        count += 1
        continue

    success , image = cap.read()
    print(count)

    # print(result)

    if type(result) == type(None):
        break

    if count in [117]:
        count+=1
        continue

    if result[0] == "a":
        imageA = image
        h,  w = imageA.shape[:2]
        # imageA = imutils.resize(imageA, width=400)
        # imageA = imageA[140:170 , 60:340]
        # imageA = imutils.rotate_bound(imageA, 270)

    elif add == 0:
        print("Trigger image")
        success , image = cap.read()
        imageA = image
        # imageA = imutils.resize(imageA, width=400)
        # imageA = imageA[140:170 , 60:340]
        # imageA = imutils.rotate_bound(imageA, 270)

    else:
        imageA = result

    h,  w = imageA.shape[:2]
    newcameramtxA, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtxA,(w,h),5)
    dst = cv2.remap(imageA,mapx,mapy,cv2.INTER_LINEAR)

    # x,y,w,h = roi
    # dst = dst[y:y+h, x:x+w]
    imageA = dst

    success , image = cap.read()

    while not success:

        success , image = cap.read()
        print("waiting for success")
        break

    imageB = image
    if type(imageB) == type(None):
        continue

    h,  w = imageB.shape[:2]
    newcameramtxB, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtxB,(w,h),5)
    dst = cv2.remap(imageB,mapx,mapy,cv2.INTER_LINEAR)
    # x,y,w,h = roi
    # dst = dst[y:y+h, x:x+w]
    imageB = dst
    # imageB = imutils.resize(imageB, width=400)

    # imageB = imageB[140:180 , 50:350]

    # imageB = imutils.rotate_bound(imageB, 270)

    # stitch the images together to create a panorama
    # stitcher = Stitcher()
    # try:
    #     re = stitcher.stitch([imageA, imageB], showMatches=True)

    # except Exception:
    #     continue
    # if type(re) == type(None):
    #     print("Can't stitch the picture")
    #     continue
    # (result, vis) = re
    # result = trim(result)

    # show the images

    cv2.imshow("Image A", imageA)
    cv2.imshow("Image B", imageB)
    # cv2.imshow("Result", result)

    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

    count += 1
    add += 1
    if add == 1:
        # result = imutils.resize(result, width=400)
        list_result.append(result)
        add = 0

    # except Exception as e:

    #     print(e)
    #     break



# list_result_2 = []

# for i in range(len(list_result)-1):

#     stitcher = Stitcher()
#     try:
#         (result, vis) = stitcher.stitch([list_result[i+1], list_result[i]], showMatches=True)
#     except ValueError:
#         (result, vis) = stitcher.stitch([list_result[i], list_result[i+1]], showMatches=True)
#     except TypeError:
#         continue
#     result = trim(result)
#     list_result_2.append(result)

# # cv2.imshow("Keypoint Matches", vis)
# num = 0
# for i in list_result_2:
#     # cv2.imshow("Result form list "+str(num), i)
#     # image_namee = "/home/pat/HG_internship/MobileRobot/video/image_group/image"+str(num)+".png"
#     # cv2.imwrite(image_namee,i)
#     # num += 1



# list_result_3 = []

# for i in range(len(list_result)-1):

#     stitcher = Stitcher()
#     try:
#         (result, vis) = stitcher.stitch([list_result[i+1], list_result[i]], showMatches=True)
#     except ValueError:
#         (result, vis) = stitcher.stitch([list_result[i], list_result[i+1]], showMatches=True)
#     except TypeError:
#         continue
#     result = trim(result)
#     list_result_2.append(result)

# # cv2.imshow("Keypoint Matches", vis)
# num = 0
# for i in list_result_2:
#     cv2.imshow("Result form list "+str(num), i)
#     image_namee = "/home/pat/HG_internship/MobileRobot/video/image_group/image"+str(num)+".png"
#     cv2.imwrite(image_namee,i)
#     num += 1

# cv2.imshow("Result", result)
# cv2.waitKey(0)