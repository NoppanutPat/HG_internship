import cv2
import numpy as np

def image_locate(number):
    return "/home/pat/HG_internship/MobileRobot/video/006/batch_"+number+".png" 

samples = []
pattern_size = (6,9)

for i in range(1,500):

    if i % 21 == 0:
        continue

    image_number = "{:03}".format(i%21)

    # print(image_locate(image_number))

    frame = cv2.imread(image_locate(image_number))

    res, corners = cv2.findChessboardCorners(frame, pattern_size)

    print(res , corners)

    img_show = np.copy(frame)
    cv2.drawChessboardCorners(img_show,pattern_size,corners,res)

    cv2.putText(img_show, "Samples captured: %d" % len(samples) , (0,40) , cv2.FONT_HERSHEY_SIMPLEX , 1.0,(0,255,0),2)

    cv2.imshow('chessboard',img_show)

    wait_time = 0 if res else 30

    k = cv2.waitKey(wait_time)
    if k == ord("s") and res:

        samples.append((cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),corners))

    elif k == 27:
        break

cv2.destroyAllWindows()
    