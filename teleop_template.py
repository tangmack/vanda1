#!/usr/bin/env python
import rospy

from std_msgs.msg import Float64

import sys, select, termios, tty

# msg = """
# Control Your Toy!
# ---------------------------
# Moving around:
#    u    i    o
#    j    k    l
#    m    ,    .
# q/z : increase/decrease max speeds by 10%
# w/x : increase/decrease only linear speed by 10%
# e/c : increase/decrease only angular speed by 10%
# space key, k : force stop
# anything else : stop smoothly
# CTRL-C to quit
# """


msg = """
Control Your Toy!
---------------------------
Moving around:
   q    w    e
   a    s    d
   z         c

   spacebar = stop

k/j : increase/decrease max speeds by 10%

m/n : increase/decrease only linear speed by 10%
./, : increase/decrease only angular speed by 10%
space key : force stop
anything else : stop smoothly
CTRL-C to quit
"""

# moveBindings = {
#         'i':(-1,0),
#         'o':(-1,-1),
#         'j':(0,1),
#         'l':(0,-1),
#         'u':(-1,1),
#         ',':(1,0),
#         '.':(-1,1),
#         'm':(-1,-1),
#            }

moveBindings = {
        'w':(-1,0),
        'e':(-1,-1),
        'a':(0,1),
        'd':(0,-1),
        'q':(-1,1),
        's':(1,0),
        'c':(-1,1),
        'z':(-1,-1),
           }
# speedBindings={
#         'q':(1.1,1.1),
#         'z':(.9,.9),
#         'w':(1.1,1),
#         'x':(.9,1),
#         'e':(1,1.1),
#         'c':(1,.9),
#           }

speedBindings={
        'k':(1.1,1.1),
        'j':(.9,.9),
        'm':(1.1,1),
        'n':(.9,1),
        '.':(1,1.1),
        ',':(1,.9),
          }

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

speed = 17.0
turn = 0.7

def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)
    
    rospy.init_node('turtlebot_teleop')

    pub_right = rospy.Publisher('/vanda1robot/axle_L_c/command', Float64, queue_size=10) # Add your topic here between ''. Eg '/my_robot/steering_controller/command'
    rate = rospy.Rate(100.0) # 10hz

    pub_left = rospy.Publisher('/vanda1robot/axle_R_c/command', Float64, queue_size=10)
    rate = rospy.Rate(100.0) # 10hz


    # -- Add front wheel steering for all wheel drive. Competition world floor is too slippery, get better traction for turns this way
    pub_wheel_L = rospy.Publisher('/vanda1robot/wheel_L_c/command', Float64, queue_size=10) # Add your topic for move here '' Eg '/my_robot/longitudinal_controller/command'
    rate = rospy.Rate(100.0) # 10hz
    pub_wheel_R = rospy.Publisher('/vanda1robot/wheel_R_c/command', Float64, queue_size=10) # Add your topic for move here '' Eg '/my_robot/longitudinal_controller/command'
    rate = rospy.Rate(100.0) # 10hz
    # --


    # Rear wheel controller
    pub_move = rospy.Publisher('/vanda1robot/rear_c/command', Float64, queue_size=10) # Add your topic for move here '' Eg '/my_robot/longitudinal_controller/command'
    rate = rospy.Rate(100.0) # 10hz



    x = 0
    th = 0
    status = 0
    count = 0
    acc = 0.1
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_turn = 0
    try:
        print msg
        print vels(speed,turn)
        while(1):
            key = getKey()
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                th = moveBindings[key][1]
                count = 0
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]
                count = 0

                print vels(speed,turn)
                if (status == 14):
                    print msg
                status = (status + 1) % 15
            elif key == ' ' or key == 'k' :
                x = 0
                th = 0
                control_speed = 0
                control_turn = 0
            else:
                count = count + 1
                if count > 4:
                    x = 0
                    th = 0
                if (key == '\x03'):
                    break

            target_speed = speed * x
            target_turn = turn * th

            control_speed = target_speed
            control_turn = target_turn

            # if target_speed > control_speed:
            #     control_speed = min( target_speed, control_speed + 0.02 )
            # elif target_speed < control_speed:
            #     control_speed = max( target_speed, control_speed - 0.02 )
            # else:
            #     control_speed = target_speed

            # if target_turn > control_turn:
            #     control_turn = min( target_turn, control_turn + 0.1 )
            # elif target_turn < control_turn:
            #     control_turn = max( target_turn, control_turn - 0.1 )
            # else:
            #     control_turn = target_turn

            pub_right.publish(control_turn) # publish the turn command.
            pub_left.publish(control_turn) # publish the turn command.

            ### add all wheel drive capability
            pub_wheel_L.publish(control_speed) # publish the turn command.
            pub_wheel_R.publish(-control_speed) # publish the turn command.
            ###

            pub_move.publish(control_speed) # publish the control speed.

            rate.sleep() 


    except:
        print e

    finally:
        pub_right.publish(control_turn)
        pub_left.publish(control_turn)

        # -- add all wheel drive capability
        pub_wheel_L.publish(control_speed)
        pub_wheel_R.publish(-control_speed)
        # --

        pub_move.publish(control_speed)
        # twist = Twist()
        # twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        # twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        # pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)