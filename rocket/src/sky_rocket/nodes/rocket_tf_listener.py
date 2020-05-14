#!/usr/bin/env python  

import roslib
roslib.load_manifest('sky_rocket')
import rospy
import tf
from std_msgs.msg import Float64MultiArray

if __name__ == "__main__":
    
    rospy.init_node('rocket_tf_listener')

    rospy.loginfo("TF listener is starting!!")

    listener = tf.TransformListener()

    rocket_position = rospy.Publisher("/rocket_after_tf",Float64MultiArray,queue_size=10)

    rate = rospy.Rate(10.0)

    while not rospy.is_shutdown():

        try:
            (trans,rot) = listener.lookupTransform('/world','/rocket',rospy.Time(0))

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue

        data = trans + rot

        data = Float64MultiArray(data=data)

        rocket_position.publish(data)

        rate.sleep()

    
