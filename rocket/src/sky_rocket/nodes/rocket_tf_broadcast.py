#!/usr/bin/env python  

import roslib
roslib.load_manifest('sky_rocket')
import rospy
import tf
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Pose,Twist
from std_msgs.msg import Float64MultiArray
import numpy as np 
import message_filters


def handle_model_pose(msg):

    br = tf.TransformBroadcaster()
    br.sendTransform((msg.position.x,msg.position.y,msg.position.z),np.array([msg.orientation.x,msg.orientation.y,msg.orientation.z,msg.orientation.w])
        ,rospy.Time.now(),"world","rocket")

def state_handle(model_states , direction):

    try:
        msg = model_states.pose[1]
        direction = direction.data
        trust = direction[0]
        msg.position.z += trust
        quaternion = tf.transformations.quaternion_from_euler(direction[1],direction[2],direction[3])
        msg.orientation.x = quaternion[0]
        msg.orientation.y = quaternion[1]
        msg.orientation.z = quaternion[2]
        msg.orientation.w = quaternion[3]

        handle_model_pose(msg)

    except IndexError:
        pass


if __name__ == "__main__":
    
    rospy.init_node("rocket_tf_broadcast")
    rospy.loginfo("TF broadcast is starting!!")

    # rospy.Subscriber("/rocket_direction",Float64MultiArray,callback)

    model_states = message_filters.Subscriber('/gazebo/model_states',ModelStates)
    direction = message_filters.Subscriber("/rocket_direction",Float64MultiArray)

    ts = message_filters.ApproximateTimeSynchronizer([model_states,direction],10,0.1,allow_headerless=True)

    ts.registerCallback(state_handle)

    rospy.spin()