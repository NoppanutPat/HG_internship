#!/usr/bin/env python


import PID
import rospy
from geometry_msgs.msg import Wrench
from gazebo_msgs.msg import ModelStates
from std_msgs.msg import Float64
import time
import os

rospy.init_node("pid_control_velo",anonymous=True)
pub = rospy.Publisher("/base_force",Wrench,queue_size=10)

set_point_pub = rospy.Publisher("set_point_v",Float64,queue_size=10)
velo_pub = rospy.Publisher("real_velo",Float64,queue_size=10)

rate = rospy.Rate(50000)

def calculate_velo(velocity):

    MAX_THRUST = 7607000
    MIN_THRUST = 0

    pid.update(velocity)

    output_alt = pid.output

    if output_alt > MAX_THRUST:

        output_alt = MAX_THRUST

    if output_alt < MIN_THRUST:

        output_alt = MIN_THRUST 

    force = Wrench()
    force.force.z = output_alt

    print(force)
    pub.publish(force)

def callback_state(data):

    order = data.name.index("rocket")

    # position_list.append(data.pose[order].position.z)

    velocity = data.twist[order].linear.z

    print("velocity : ",velocity)
    # print("old velocity : ",old_velo)
    # print("Time : ",diff_time)

    set_point_pub.publish(pid.SetPoint)
    velo_pub.publish(velocity)

    calculate_velo(velocity)

    rate.sleep()

def test_pid(P, I ,D):

    global pid

    pid = PID.PID(P , I , D)

    pid.setSampleTime(0.01)

    pid.SetPoint = 10

    rospy.Subscriber("/gazebo/model_states",ModelStates,callback_state)

    rospy.spin()

if __name__ == "__main__":

    p = 10000000
    i = 2*p/100
    d = 1.45/1000*i


    test_pid(p , i , d)
