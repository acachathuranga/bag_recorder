#!/usr/bin/env python
# license removed for brevity
import rospy
from std_srvs.srv._SetBool import SetBool, SetBoolRequest, SetBoolResponse
import subprocess, shlex
import os, signal

rosbag_proc = None

def terminate_ros_node(s):
    list_cmd = subprocess.Popen("rosnode list", shell=True, stdout=subprocess.PIPE)
    list_output = list_cmd.stdout.read()
    retcode = list_cmd.wait()
    assert retcode == 0, "List command returned %d" % retcode
    for str in list_output.split("\n"):
        if (str.startswith(s)):
            os.system("rosnode kill " + str)


def terminate_process_and_children(p):
    ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % p.pid, shell=True, stdout=subprocess.PIPE)
    ps_output = ps_command.stdout.read()
    retcode = ps_command.wait()
    assert retcode == 0, "ps command returned %d" % retcode
    for pid_str in ps_output.split("\n")[:-1]:
            os.kill(int(pid_str), signal.SIGINT)
    p.terminate()

def recordBag(req):
    global rosbag_proc
    if (req.data == True):
        # # command = "rosbag record -O subset /camera/depth/image_raw /camera/rgb/image_raw /joy /mobile_base/sensors/imu_data_raw"
        command = "rosbag record -a"
        # command = shlex.split(command)
        # rosbag_proc = subprocess.Popen(command)
        rosbag_proc = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True, cwd="/home/sutd/Bag")
        msg = "Started recording"
    else:
        if (rosbag_proc != None):
            terminate_ros_node("/record")
            # terminate_process_and_children(rosbag_proc)
            # rosbag_proc.send_signal(subprocess.signal.SIGINT)
        msg = "Stopped recording"
    print (msg)
    return SetBoolResponse(True, msg)

def bag_recorder():
    rospy.init_node('bag_recorder')
    s = rospy.Service('record_bag', SetBool, recordBag)
    print ("Bag Recorder Ready!")
    rospy.spin()

if __name__ == '__main__':
    try:
        bag_recorder()
    except rospy.ROSInterruptException:
        pass

