#!/usr/bin/env python

# import roslib
# roslib.load_manifest('mobile-robot-ros')

import cv2
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import imutils
import numpy as np

class PanoramicBirdEyesView():

    def __init__(self):

        rospy.init_node("panoramic_bird_eyes_view",anonymous=True)

        camera1 = rospy.Subscriber("/camera1/image_raw",Image,self.camera1_callback)
        camera2 = rospy.Subscriber("/camera2/image_raw",Image,self.camera2_callback)
        camera3 = rospy.Subscriber("/camera3/image_raw",Image,self.camera3_callback)
        camera4 = rospy.Subscriber("/camera4/image_raw",Image,self.camera4_callback)

        stitch_pub = rospy.Publisher("/stitch_image",Image,queue_size=10)

        self.camera1 = camera1
        self.camera2 = camera2
        self.camera3 = camera3
        self.camera4 = camera4
        self.stitch_pub = stitch_pub
        self.isv3 = imutils.is_cv3()
        self.cachedH = None
        self.camera1_img = None
        self.camera2_img = None
        self.camera3_img = None
        self.camera4_img = None
        self.image_scale = 0.2

    def camera1_callback(self,data):

        bridge = CvBridge()
        cv_image = bridge.imgmsg_to_cv2(data,desired_encoding='passthrough')
        cv_image = cv_image[cv_image.shape[0]-300:,:]
        newsize = (int(cv_image.shape[1]*self.image_scale) , int(cv_image.shape[0]*self.image_scale))
        cv_image = cv2.resize(cv_image,newsize)
        self.camera1_img = cv_image

    def camera2_callback(self,data):

        bridge = CvBridge()
        cv_image = bridge.imgmsg_to_cv2(data,desired_encoding='passthrough')
        cv_image = cv_image[cv_image.shape[0]-300:,:]
        newsize = (int(cv_image.shape[1]*self.image_scale) , int(cv_image.shape[0]*self.image_scale))
        cv_image = cv2.resize(cv_image,newsize)
        cv_image = imutils.rotate_bound(cv_image , 270)
        self.camera2_img = cv_image

    def camera3_callback(self,data):

        bridge = CvBridge()
        cv_image = bridge.imgmsg_to_cv2(data,desired_encoding='passthrough')
        cv_image = cv_image[cv_image.shape[0]-300:,:]
        newsize = (int(cv_image.shape[1]*self.image_scale) , int(cv_image.shape[0]*self.image_scale))
        cv_image = cv2.resize(cv_image,newsize)
        cv_image = imutils.rotate_bound(cv_image , 180)
        self.camera3_img = cv_image

    def camera4_callback(self,data):

        bridge = CvBridge()
        cv_image = bridge.imgmsg_to_cv2(data,desired_encoding='passthrough')
        cv_image = cv_image[cv_image.shape[0]-300:,:]
        newsize = (int(cv_image.shape[1]*self.image_scale) , int(cv_image.shape[0]*self.image_scale))
        cv_image = cv2.resize(cv_image,newsize)
        cv_image = imutils.rotate_bound(cv_image , 90)
        self.camera4_img = cv_image

    def converting_image(self,image):

        bridge = CvBridge()
        image_msg = bridge.cv2_to_imgmsg(image , encoding="passthrough")

    def stitch(self, images, ratio=0.75, reprojThresh=4.0):
        # unpack the images
        (imageB, imageA) = images
        # if the cached homography matrix is None, then we need to
        # apply keypoint matching to construct it
        if self.cachedH is None:
            # detect keypoints and extract
            (kpsA, featuresA) = self.detectAndDescribe(imageA)
            (kpsB, featuresB) = self.detectAndDescribe(imageB)
            # match features between the two images
            M = self.matchKeypoints(kpsA, kpsB,
            	featuresA, featuresB, ratio, reprojThresh)
            # if the match is None, then there aren't enough matched
            # keypoints to create a panorama
            if M is None:
            	return None
            # cache the homography matrix
            self.cachedH = M[1]
        # apply a perspective transform to stitch the images together
        # using the cached homography matrix
        result = cv2.warpPerspective(imageA, self.cachedH,
            (imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
        result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB
        # return the stitched image
        return result
    
    def detectAndDescribe(self, image):
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # check to see if we are using OpenCV 3.X
        if self.isv3:
        	# detect and extract features from the image
        	descriptor = cv2.xfeatures2d.SIFT_create()
        	(kps, features) = descriptor.detectAndCompute(image, None)
        # otherwise, we are using OpenCV 2.4.X
        else:
        	# detect keypoints in the image
        	detector = cv2.FeatureDetector_create("SIFT")
        	kps = detector.detect(gray)
        	# extract features from the image
        	extractor = cv2.DescriptorExtractor_create("SIFT")
        	(kps, features) = extractor.compute(gray, kps)
        # convert the keypoints from KeyPoint objects to NumPy
        # arrays
        kps = np.float32([kp.pt for kp in kps])
        # return a tuple of keypoints and features
        return (kps, features)

    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB,
        ratio, reprojThresh):
        # compute the raw matches and initialize the list of actual
        # matches
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []
        # loop over the raw matches
        for m in rawMatches:
        	# ensure the distance is within a certain ratio of each
        	# other (i.e. Lowe's ratio test)
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))
        # computing a homography requires at least 4 matches
        if len(matches) > 4:
        	# construct the two sets of points
        	ptsA = np.float32([kpsA[i] for (_, i) in matches])
        	ptsB = np.float32([kpsB[i] for (i, _) in matches])
        	# compute the homography between the two sets of points
        	(H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                reprojThresh)
        	# return the matches along with the homograpy matrix
        	# and status of each matched point
        	return (matches, H, status)
        # otherwise, no homograpy could be computed
        return None        

    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
        # initialize the output visualization image
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB
        # loop over the matches
        for ((trainIdx, queryIdx), s) in zip(matches, status):
        	# only process the match if the keypoint was successfully
        	# matched
            if s == 1:
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)
        # return the visualization
        return vis

    def panoramic_stitch(self):

        width = int(1920*0.5)
        height = int(1920*0.5)

        image1 = np.zeros((height,width,3), np.uint8)
        image2 = np.zeros((height,width,3), np.uint8)
        a = (self.camera1_img,self.camera2_img,self.camera3_img,self.camera4_img)

        for i in a:
            if i is None:
                return (image1,image1,image1,image1)

        return a

if __name__ == "__main__":
    
    panoramic = PanoramicBirdEyesView()

    while not rospy.is_shutdown():

        (image1 , image2 , image3 , image4) = panoramic.panoramic_stitch()

        cv2.imshow("Image1",image1)
        cv2.imshow("Image2",image2)
        cv2.imshow("Image3",image3)
        cv2.imshow("Image4",image4)

        if cv2.waitKey(1) == ord('q'):
            break


        

