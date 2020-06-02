import numpy as np
import matplotlib.image
import math
import cv2

def sigmoid(x):
  y = np.zeros(len(x))
  for i in range(len(x)):
    y[i] = 1 / (1 + math.exp(-x[i]))
  return y

sigmoid_ = sigmoid(np.arange(-1, 1, 1/50))
alpha = np.repeat(sigmoid_.reshape((len(sigmoid_), 1)), repeats=100, axis=1)

image1_connect = np.ones((1, 300))
image2_connect = np.zeros((1, 300))
# out = image1_connect * (1.0 - alpha) + image2_connect * alpha
out = cv2.addWeighted(image1_connect,0,image2_connect,1.0,0)
# matplotlib.image.imsave('blend.png', out, cmap = 'gray')
cv2.imshow("out",out)
cv2.waitKey(0)