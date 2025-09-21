#!/usr/bin/env python3
#coding=utf8
import sys
import asyncio
import multiprocessing
import enum 

sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos  import Servos
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')
from motors  import Motors
sys.path.append('/home/tah/GitHub/TAH-ROBOT/gamepad')
from gamepad import Gamepad
sys.path.append('/home/tah/GitHub/TAH-ROBOT/camera')
from camera  import Camera
sys.path.append('/home/tah/GitHub/TAH-ROBOT/pid')
from pid  import MyPID

class PROCESS_ACTION(enum.Enum):
    KILL_THREAD = object() 
    LOST_OBJECT = object()

# -------------------------------------------
def robot_servo(servos_instance : Servos,
                vision_queue : type[multiprocessing.JoinableQueue]):
    
    pidx = MyPID(0.15,0.0,0.005)
    sx = servos_instance.servo0.angle

    (width,height) = vision_queue.get()
    vision_queue.task_done()
    assert (width,height)==(800,480) , print("First data in servo queue is not the width/height.")
    cX = width/2.0
    cY = height/2.0
    
    while True:
        data = vision_queue.get()
        if data is PROCESS_ACTION.KILL_THREAD:
            vision_queue.task_done()
            break
        elif data is PROCESS_ACTION.LOST_OBJECT:
            pass
        else :
            move_x = pidx.pid(cX, data[0], data[3])
            new_x = int(sx + move_x)
            if new_x < 0 or new_x > 180: 
                #position_x = int(servo_x - control/4.0) 
                new_x = sx
            servos_instance.servo0.angle = new_x
            print(new_x)
        #------
        vision_queue.task_done()
    return
# -------------------------------------------

# -------------------------------------------
def robot_see(battery_queue : type[multiprocessing.JoinableQueue],
              tracking_queue : type[multiprocessing.JoinableQueue]):
    my_camera = Camera(battery_queue  = battery_queue,
                       tracking_queue = tracking_queue)
    my_camera.track()
    my_camera.deinit()
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

    servo_queue = multiprocessing.JoinableQueue()
    vision_process = multiprocessing.Process(target=robot_see, args=(my_battery, servo_queue,))
    servo_process = multiprocessing.Process(target=robot_servo, args=(my_servos, servo_queue,))
    vision_process.start()
    servo_process.start()

    gamepad_loop   = asyncio.get_running_loop()
    future = await asyncio.gather(my_gamepad.event_loop(),
                                  my_gamepad.drive_loop(),
                                  my_gamepad.battery_loop())  
    
    vision_process.terminate()
    servo_queue.put(PROCESS_ACTION.KILL_THREAD)
    servo_process.join()
    my_servos.deinit()
    my_motors.deinit()
# -------------------------------------------

# -------------------------------------------
if __name__ == "__main__":
    asyncio.run(follow_control())




