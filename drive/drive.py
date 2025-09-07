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

def robot_see(my_motors : Motors):
    my_camera = Camera()
    my_camera.start()
    #my_camera.deinit()

async def gamepad_control() :
    my_servos  = Servos()
    my_motors  = Motors()
    my_gamepad = Gamepad(servos_instance=my_servos, motors_instance=my_motors)

    vision_process = multiprocessing.Process(target=robot_see, args=(my_motors))
    vision_process.start()

    gamepad_loop   = asyncio.get_running_loop()
    future = await asyncio.gather(my_gamepad.run_00(),my_gamepad.run_01())  
    
    vision_process.terminate()
    my_servos.deinit()
    my_motors.deinit()

if __name__ == "__main__":
    asyncio.run(gamepad_control())




