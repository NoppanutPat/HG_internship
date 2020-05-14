#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Wrench
from std_msgs.msg import Float64 , Float64MultiArray
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np 
from gazebo_msgs.msg import ModelStates
import tf
import time


status = 0
define_x = -1000
define_y = -1000
current_alt = 0
current_row = -100
current_pitch = -100
last_sender = [-100,-100,-100]
finish = 0

rospy.init_node("Goto_target",anonymous=True)
set_alt = rospy.Publisher("/set_alt",Float64,queue_size=10)
set_attitude = rospy.Publisher("/set_attitude",Float64MultiArray,queue_size=10)
set_vel = rospy.Publisher("/set_vel",Float64,queue_size=10)
rate = rospy.Rate(10)

def detect(image):

    output = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # image = cv2.blur(image, (3, 3)) 

    cv2.imshow("Frame",image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        global status
        status = 10

    rows = image.shape[0]

    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, rows / 8 ,param1=100, param2=30,minRadius=1, maxRadius=80000)

    global define_x , define_y
    define_x = -1000
    define_y = -1000

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            define_x = x - 400
            define_y = -(y - 400)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        cv2.imshow("output", output)
        if cv2.waitKey(1) and (0xFF == ord('q') or 0xFF == ord('Q')):
            print("Status = ",status)
            global status
            status = 10

def rocket_control():

    MAX_PITCH = 0.03
    MIN_PITCH = -0.03
    MAX_ROW = -0.03
    MIN_ROW = 0.03

    if define_x == -1000 and define_y == -1000:

        set_vel.publish(0)
        # set_attitude.publish(Float64MultiArray(data=[0,0,0]))

        return 0
    # print  "y : ",define_y ," , x : ",define_x

    if finish == 1:

        print("Finish!!!!!!!!!!!")

        while not (current_alt > 165*0.95 and current_alt < 165*1.05):
            set_alt.publish(165)
            print("current_alt : ",current_alt)
            continue

        time.sleep(10)

        global status
        status = 1

    max_range_define_x = 800
    min_range_define_x = 50

    max_range_define_y = 800
    min_range_define_y = 100

    if define_x > max_range_define_x:

        pitch = MAX_PITCH

    elif define_x < -max_range_define_x:

        pitch = MIN_PITCH

    elif define_x < max_range_define_x and define_x > min_range_define_x:

        pitch = -(MAX_PITCH * define_x) / max_range_define_x

        if pitch > MAX_PITCH:
            pitch = MAX_PITCH
        elif pitch < MIN_PITCH:
            pitch = MIN_PITCH

    elif define_x > -max_range_define_x and define_x < -min_range_define_x:

        pitch = (MIN_PITCH * define_x) / max_range_define_x
        if pitch > MAX_PITCH:
            pitch = MAX_PITCH
        elif pitch < MIN_PITCH:
            pitch = MIN_PITCH

    else:

        pitch = 0

    if define_y > max_range_define_y:

        row = MAX_ROW

    elif define_y < -max_range_define_y:

        row = MIN_ROW

    elif define_y < max_range_define_y and define_y > min_range_define_y:

        row = (MAX_ROW * define_y) / max_range_define_y
        if row < MAX_ROW:
            row = MAX_ROW
        elif row > MIN_ROW:
            row = MIN_ROW

    elif define_y > -max_range_define_y and define_y < -min_range_define_y:

        row = -(MIN_ROW * define_y) / max_range_define_y
        if row < MAX_ROW:
            row = MAX_ROW
        elif row > MIN_ROW:
            row = MIN_ROW

    else:

        row = 0

    if current_row == -100 and current_pitch == -100:

        att = Float64MultiArray(data=[row,pitch,0])
        print "Att : ",att.data
        set_attitude.publish(att)
        global last_sender
        last_sender = att.data

    elif not (-100 in last_sender): #for steady state

        if abs(current_row - last_sender[0]) < 10**-4:

            if abs(current_pitch - last_sender[1]) < 10**-4:

                att = Float64MultiArray(data=[row,pitch,0])
                print "Att : ",att.data
                set_attitude.publish(att)
                global last_sender
                last_sender = att.data
            
            else:

                print("pitch and row is not ready!!")
                print("current_row : ",current_row,"current_pitch : ",current_pitch)
                print("last_row : ",last_sender[0],"last_pitch : ",last_sender[1])

        else:

            print("row is not ready!!")
            print("current_row : ",current_row,"current_pitch : ",current_pitch)
            print("last_row : ",last_sender[0],"last_pitch : ",last_sender[1])
    
    else:

        att = Float64MultiArray(data=[row,pitch,0])
        print "Att : ",att.data
        set_attitude.publish(att)
        global last_sender
        last_sender = att.data


    if row == 0 and pitch == 0 and current_row > -10**-5 and current_row < 10**-5 and current_pitch > -10**-5 and current_pitch < 10**-5:
        set_alt.publish(165)
        # set_vel.publish(10.0)
        global finish
        finish = 1

    else:
        set_alt.publish(50)

    rate.sleep()
    
def landing_control():

    print("landing!!!")

    att = Float64MultiArray(data=[0,0,0])    
    set_attitude.publish(att)
    while not (current_row > -5*10**-5 and current_row < 5*10**-5 and current_pitch > -5*10**-5 and current_pitch < 5*10**-5) and status == 1:
        print("current_row : ",current_row,"current_pitch : ",current_pitch)
        continue

    for i in range(int(current_alt) , -9 , -10):

        if status == 10:
            return 0

        if i < 0:

            print("Alt : 0")
        else:
        
            print("Alt : ",i)

        set_alt.publish(i)

        time.sleep(2)

    while current_alt > -10**-4 and current_alt < 10**-4:

        if status == 10:
            return 0

        continue

    global status
    status = 2



# def move_rocket():

#     force_apply = Wrench()

#     max_range_define = 0.5

#     if define_x == -100 and define_y == -100:
        
#         force_apply.force.z = 2300000

#         body_force.publish(force_apply)

#         rate.sleep()
        
#         return 0

#     if define_x > max_range_define:

#         force_apply.torque.y = 10000

#     elif define_x < max_range_define:

#         force_apply.torque.y = -10000

#     if define_y > max_range_define:

#         force_apply.torque.x = -10000

#     elif define_y < max_range_define:

#         force_apply.torque.x = 10000

#     if force_apply.torque.x == 0 and force_apply.torque.y == 0:

#         force_apply.force.z = 4000000

#     else:

#         force_apply.force.z = 2300000


#     print(force_apply)

#     body_force.publish(force_apply)

#     global define_x , define_y

#     define_x = -100
#     define_y = -100

#     rate.sleep()

def update_state(data):

    order = data.name.index("rocket")
    global current_alt , current_row , current_pitch
    current_alt = data.pose[order].position.z
    euler = tf.transformations.euler_from_quaternion([data.pose[order].orientation.x,data.pose[order].orientation.y,data.pose[order].orientation.z,data.pose[order].orientation.w])
    current_row = euler[0]
    current_pitch = euler[1]

def callback_image(msg):

    bridge = CvBridge()
    frame = bridge.imgmsg_to_cv2(msg, "bgr8")
    detect(frame)




def listenner():

    rospy.Subscriber("/camera1/image_raw",Image,callback_image)
    rospy.Subscriber("/gazebo/model_states" , ModelStates , update_state)
    global status
    while status == 0:
        rocket_control()
        continue
    while status == 1:
        landing_control()
        continue 

if __name__ == "__main__":
    
    listenner()