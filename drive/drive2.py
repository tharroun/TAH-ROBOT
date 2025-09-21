#!/usr/bin/env python3
#coding=utf8
import evdev
import math
import sys
import asyncio
import multiprocessing
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos import Servos
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')
from motors import Motors
sys.path.append('/home/tah/GitHub/TAH-ROBOT/gamepad')
from gamepad2 import Gamepad

# -----------------------------------
async def event_loop(gamepad : Gamepad,
                     servos  : Servos) -> bool:
    sx,sy=0,0
    async for event in gamepad.gamepad.async_read_loop() :
        if event.code == evdev.ecodes.BTN_MODE and event.value == 0:
            gamepad.running = False
            break

        if event.type ==  evdev.ecodes.EV_ABS :
            if event.code == evdev.ecodes.ABS_RY : 
                sy=event.value
                _update_servos(gamepad,servos,sx,sy)
            if event.code == evdev.ecodes.ABS_RX : 
                sx=event.value
                _update_servos(gamepad,servos,sx,sy)
            if event.code == evdev.ecodes.ABS_HAT0Y :
                if event.value ==  1 : gamepad.rotation_speed -= 50
                if event.value == -1 : gamepad.rotation_speed += 50
                if gamepad.rotation_speed > 900 : gamepad.rotation_speed = 900
                if gamepad.rotation_speed < 0   : gamepad.rotation_speed = 0
        
    print("Finished event_loop")
    return True
# -----------------------------------

# -----------------------------------
def _update_servos(gamepad : Gamepad,
                   servos  : Servos,
                   sx: float = 0,
                   sy: float = 0) :
    deg_x = math.trunc(gamepad.servos_mx*sx+gamepad.servos_bx)
    deg_y = math.trunc(gamepad.servos_my*sy+gamepad.servos_by)
    servos.servo0.angle = deg_x
    servos.servo1.angle = deg_y
    return
# -----------------------------------

# -----------------------------------
async def drive_loop(gamepad : Gamepad,
                     motors : Motors) -> bool:
    omega = 0
    while gamepad.running :
        mx = gamepad.gamepad.absinfo(evdev.ecodes.ABS_X).value
        my = gamepad.gamepad.absinfo(evdev.ecodes.ABS_Y).value
            
        rcw  = gamepad.gamepad.absinfo(evdev.ecodes.ABS_RZ).value
        rccw = gamepad.gamepad.absinfo(evdev.ecodes.ABS_Z).value
        if rcw == 255 and rccw == 0   : omega = gamepad.rotation_speed
        elif rcw == 0 and rccw == 255 : omega = -gamepad.rotation_speed
        else : omega = 0

        speed_x = gamepad.motors_mx*math.fabs(mx)
        speed_y = gamepad.motors_my*math.fabs(my)
        speed = math.sqrt(speed_x*speed_x+speed_y*speed_y)
        direction = math.atan2(mx,my)*180.0/math.pi + 180.0
        motors.go(speed,direction,omega)
        await asyncio.sleep(0.1)
    motors.stop()
    print("Finished drive_loop")
    return True
# -----------------------------------


# -----------------------------------
async def battery_loop(gamepad: Gamepad,
                       motors : Motors) -> bool:
    while gamepad.running :
        volts = motors.get_battery()
        print(f"Motor voltage: {volts}")
        await asyncio.sleep(2.0)
    print("Finished battery_loop")
    return True
#-----------------------------------

#-----------------------------------
async def gamepad_main_loop(my_servos : Servos,
                            my_motors : Motors,
                            my_gamepad : Gamepad) :
    loop   = asyncio.get_running_loop()
    future = await asyncio.gather(event_loop(my_gamepad,my_servos),
                                  drive_loop(my_gamepad,my_motors),
                                  battery_loop(my_gamepad,my_motors)) 
    print("Finished gamepad_main_loop")
#-----------------------------------

#-----------------------------------
def robot_control(my_servos : Servos,
                  my_motors : Motors,
                  my_gamepad : Gamepad) :
    asyncio.run(gamepad_main_loop(my_servos,my_motors,my_gamepad))
    print("Finished robot_control")
    return
#-----------------------------------
if __name__ == "__main__":
    
    my_servos  = Servos()
    my_motors  = Motors()
    my_gamepad = Gamepad()

    gamepad_process = multiprocessing.Process(target=robot_control, args=(my_servos,my_motors,my_gamepad,))
    gamepad_process.start()

    #vision_process = multiprocessing.Process(target=robot_see, args=(my_battery,))
    #vision_process.start()

    gamepad_process.join()
    my_servos.deinit()
    my_motors.deinit()
    my_gamepad.deinit()





