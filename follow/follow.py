#!/usr/bin/env python3
#coding=utf8
import sys
import asyncio
import signal
import functools
import multiprocessing
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos  import Servos
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')
from motors  import Motors
sys.path.append('/home/tah/GitHub/TAH-ROBOT/gamepad')
from gamepad import Gamepad
sys.path.append('/home/tah/GitHub/TAH-ROBOT/camera')
from camera  import Camera

# -------------------------------------------
def robot_servo(servos_instance : Servos | None = None,
                vision_queue : type[multiprocessing.JoinableQueue]):
    return
# -------------------------------------------

# -------------------------------------------
def robot_see(battery_queue : type[multiprocessing.JoinableQueue],
              tracking_queue : type[multiprocessing.JoinableQueue] | None):
    my_camera = Camera(battery_queue  = battery_queue,
                       tracking_queue = tracking_queue)
    my_camera.track()
    #my_camera.deinit()
    return
# -------------------------------------------

# -------------------------------------------
async def follow_control() :
    my_servos  = Servos()
    my_motors  = Motors()
    my_battery = multiprocessing.JoinableQueue()
    my_gamepad = Gamepad(servos_instance = my_servos, 
                         motors_instance = my_motors,
                         battery_queue   = my_battery)

    my_tracking = multiprocessing.JoinableQueue()
    vision_process = multiprocessing.Process(target=robot_see, args=(my_battery, my_tracking,))
    vision_process.start()
    servo_process = multiprocessing.Process(target=robot_servo, args=(my_servos, my_tracking,))
    servo_process.start()

    gamepad_loop   = asyncio.get_running_loop()
    future = await asyncio.gather(my_gamepad.event_loop(),
                                  my_gamepad.drive_loop(),
                                  my_gamepad.battery_loop())  
    
    vision_process.terminate()
    servo_process.terminate()
    my_servos.deinit()
    my_motors.deinit()
# -------------------------------------------

# -------------------------------------------
if __name__ == "__main__":
    asyncio.run(follow_control())




