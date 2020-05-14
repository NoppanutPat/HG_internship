#!/usr/bin/env python

import roslib
roslib.load_manifest('sky_rocket')
import PID
import rospy
from geometry_msgs.msg import Wrench , Pose
from gazebo_msgs.msg import ModelStates
from std_msgs.msg import Float64 , Float64MultiArray
from std_srvs.srv import Empty , EmptyResponse
import matplotlib
import time
from tf.transformations import euler_from_quaternion

rospy.init_node("pid_control",anonymous=True)
pub = rospy.Publisher("/engine_force",Wrench,queue_size=10)
set_point_alt = rospy.Publisher("/set_point_alt",Float64,queue_size=10)
set_point_row = rospy.Publisher("/set_point_row",Float64,queue_size=10)
set_point_pitch = rospy.Publisher("/set_point_pitch",Float64,queue_size=10)
set_point_yaw = rospy.Publisher("/set_point_yaw",Float64,queue_size=10)
set_point_vel = rospy.Publisher("/set_point_vel",Float64,queue_size=10)

alt_state = rospy.Publisher("/model_alt_point",Float64,queue_size=10)
row_state = rospy.Publisher("/model_row_point",Float64,queue_size=10)
pitch_state = rospy.Publisher("/model_pitch_point",Float64,queue_size=10)
yaw_state = rospy.Publisher("/model_yaw_point",Float64,queue_size=10)
vel_state = rospy.Publisher("/model_vel_point",Float64,queue_size=10)


def reset_pid(req):

    global reset
    reset = 1
    print("Reset!!!")
    return EmptyResponse()

rospy.Service("reset_pid",Empty,reset_pid)

def check_feedback(feedback_alt , feedback_row , feedback_pitch , feedback_yaw , feedback_vel):

    MAX_THRUST = 7607000
    MIN_THRUST = 0

    MAX_JET = 20000000
    MIN_JET = -20000000


    pid_alt.update(feedback_alt)
    pid_row.update(feedback_row)
    pid_pitch.update(feedback_pitch)
    pid_yaw.update(feedback_yaw)
    pid_vel.update(feedback_vel)

    output_alt = pid_alt.output
    output_row = pid_row.output
    output_pitch = pid_pitch.output
    output_yaw = pid_yaw.output
    output_vel = pid_vel.output

    if output_alt > MAX_THRUST:

        output_alt = MAX_THRUST

    elif output_alt < MIN_THRUST:
        
        output_alt = MIN_THRUST

    if output_vel > MAX_THRUST:

        output_vel = MAX_THRUST

    elif output_vel < MIN_THRUST:
        
        output_vel = MIN_THRUST

    if output_row > MAX_JET:

        output_row = MAX_JET

    elif output_row < MIN_JET:
        
        output_row = MIN_JET

    if output_pitch > MAX_JET:

        output_pitch = MAX_JET

    elif output_pitch < MIN_JET:
        
        output_pitch = MIN_JET

    if output_yaw > MAX_JET:

        output_yaw = MAX_JET

    elif output_yaw < MIN_JET:
        
        output_yaw = MIN_JET

    force = Wrench()
    force.force.z = output_alt
    if pid_alt.SetPoint == -1:
        force.force.z = output_vel
    force.torque.x = output_row
    force.torque.y = output_pitch
    force.torque.z = output_yaw

    print("Publish force :",force)
    pub.publish(force)

def callback_state(data):

    order = data.name.index("rocket")

    feedback_alt = data.pose[order].position.z
    feedback_vel = data.twist[order].linear.z
    q = (data.pose[order].orientation)
    euler = euler_from_quaternion((q.x , q.y , q.z , q.w))

    set_point_alt.publish(pid_alt.SetPoint)
    set_point_row.publish(pid_row.SetPoint)
    set_point_pitch.publish(pid_pitch.SetPoint)
    set_point_yaw.publish(pid_yaw.SetPoint)
    set_point_vel.publish(pid_vel.SetPoint)

    alt_state.publish(feedback_alt)
    row_state.publish(euler[0])
    pitch_state.publish(euler[1])
    yaw_state.publish(euler[2])
    vel_state.publish(feedback_vel)

    print("Alt : ",feedback_alt , "Row : ", euler[0] , "Pitch : ", euler[1] , "Yaw : ", euler[2],"Vel : ",feedback_vel)
    check_feedback(feedback_alt, euler[0] , euler[1] , euler[2] , feedback_vel)

def setpoint_attitude(data):

    euler = data.data
    
    pid_row.SetPoint = euler[0]
    pid_pitch.SetPoint = euler[1]
    pid_yaw.SetPoint = euler[2]

def setpoint_alt(data):

    pid_alt.SetPoint = data.data

def setpoint_vel(data):

    pid_vel.SetPoint = data.data

def test_pid(PID_alt, PID_row , PID_pitch , PID_yaw , PID_vel):

    global pid_alt , pid_row , pid_pitch , pid_yaw , pid_vel

    pid_alt = PID.PID(PID_alt[0],PID_alt[1],PID_alt[2])
    pid_row = PID.PID(PID_row[0],PID_row[1],PID_row[2])
    pid_pitch = PID.PID(PID_pitch[0],PID_pitch[1],PID_pitch[2])
    pid_yaw = PID.PID(PID_yaw[0],PID_yaw[1],PID_yaw[2])
    pid_vel = PID.PID(PID_vel[0],PID_vel[1],PID_vel[2])


    # pid.SetPoint = 100
    pid_alt.setSampleTime(0.01)
    pid_row.setSampleTime(0.01)
    pid_pitch.setSampleTime(0.01)
    pid_yaw.setSampleTime(0.01)
    pid_vel.setSampleTime(0.01)


    rospy.Subscriber("/gazebo/model_states",ModelStates,callback_state)
    rospy.Subscriber("/set_attitude",Float64MultiArray,setpoint_attitude)
    rospy.Subscriber("/set_alt",Float64,setpoint_alt)
    rospy.Subscriber("/set_vel",Float64,setpoint_vel)

    while reset == 0:
        continue

if __name__ == "__main__":

    alt_pid = (10000000,2300000,22000000)
    row_pid = (120000000,60000,190000000)
    pitch_pid = (120000000,60000,190000000)
    # row_pid = (120000000,0,190000000)
    # pitch_pid = (120000000,0,190000000)
    yaw_pid = (600000,700,170000)
    vel_pid = (70000000 , 700000 , 500)

    while not rospy.is_shutdown():
        
        global reset
        reset = 0

        test_pid(alt_pid,row_pid,pitch_pid,yaw_pid,vel_pid)
    

