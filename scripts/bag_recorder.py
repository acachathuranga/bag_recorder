#!/usr/bin/env python
# license removed for brevity
import rospy
from std_srvs.srv._SetBool import SetBool, SetBoolRequest, SetBoolResponse
import subprocess, shlex
import os, signal

rosbag_proc = None
recorder_name = None
topics = None
directory = None

def terminate_ros_node(s):
    list_cmd = subprocess.Popen("rosnode list", shell=True, stdout=subprocess.PIPE)
    list_output = list_cmd.stdout.read()
    retcode = list_cmd.wait()
    assert retcode == 0, "List command returned %d" % retcode
    for str in list_output.split("\n"):
        if (str.startswith(s)):
            os.system("rosnode kill " + str)

def recordBag(req):
    global rosbag_proc
    if (req.data == True):
        # command = "rosbag record -O subset /camera/depth/image_raw /camera/rgb/image_raw /joy /mobile_base/sensors/imu_data_raw"
        # command = "rosbag record -a"
        topicList = ""
        for topic in topics:
            topicList += "/" + topic + " "
        
        command = "roslaunch bag_recorder node.launch node_prefix:=" + recorder_name + " directory:=" + directory + " topics:='" + topicList + "'"
        print (command)
        rosbag_proc = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True)
        msg = "Started recording"
    else:
        if (rosbag_proc != None):
            terminate_ros_node("/" + recorder_name + "_rosbag")
        msg = "Stopped recording"
    print (msg)
    return SetBoolResponse(True, msg)

def bag_recorder():
    rospy.init_node('bag_recorder', anonymous=True)
    node_name = rospy.get_name()

    # Get Parameters
    global recorder_name, topics, directory
    recorder_name = rospy.get_param(rospy.get_name()+ '/recorder_name')
    topics = rospy.get_param(rospy.get_name()+ '/topics', '-a')
    directory = rospy.get_param(rospy.get_name()+ '/directory', '/home/sutd/Bag')

    s = rospy.Service('/record_bag', SetBool, recordBag) #node_name + '/record_bag'
    print recorder_name, " : Bag Recorder Ready!"
    rospy.spin()

if __name__ == '__main__':
    try:
        bag_recorder()
    except rospy.ROSInterruptException:
        pass


