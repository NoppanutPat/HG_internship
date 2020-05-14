#!/usr/bin/env python

import rospy

from std_srvs.srv import Empty , EmptyResponse

def serviceiscalling(req):
    print("Service is calling")
    return EmptyResponse()

def main():

    rospy.init_node("test_service")
    rospy.Service("test_service",Empty,serviceiscalling)
    rospy.spin()

if __name__ == "__main__":
    
    main()