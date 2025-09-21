#!/usr/bin/env python3
#coding=utf8
import evdev
import math
import sys
import asyncio
from   multiprocessing import JoinableQueue
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos import Servos
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')
from motors import Motors

class Gamepad:
    '''
    8BitDo SN30Pro 
    Appears as X-box controller on the RPi5.
    '''
    def __init__(
        self,
    ):

        found_gamepad = False
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if 'X-Box' in device.name:
                found_gamepad = True
                break
        if found_gamepad: 
            self.gamepad = evdev.InputDevice(device.path) # type: ignore
        else :
            raise RuntimeError(f"Failed to initialize gamepad.")
        # gamepad_str = pprint.pformat(self.gamepad.capabilities(verbose=True))

        # IT SOMETIMES SEEMS THAT THE EVENTIO QUEUE NEEDS TO BE FLUSHED
        # WHEN STARTING THE PROGRAM. MAYBE IT'S ASYNCIO?
        while self.gamepad.read_one():
            pass
        self.running = True

        # - SERVOS -----
        # RIGHT STICK
        # LINEAR MAPING OF STICK (MIN,MAX) -> (0,180) PWM VALUES
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RX)
        self.servos_mx = -180.0/math.fabs(absinfo.max-absinfo.min)
        self.servos_bx = -self.servos_mx*absinfo.max
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RY)
        self.servos_my = 153.0/math.fabs(absinfo.max-absinfo.min)
        self.servos_by = -self.servos_my*absinfo.min
        
        # - MOTORS -----
        # LEFT STICK
        # LINEAR MAPING OF STICK ABS(MIN,MAX) -> (0,1500) PWM SPEED UNITS
        #self.gamepad.set_absinfo(evdev.ecodes.ABS_X,flat=10,fuzz=20)
        #self.gamepad.set_absinfo(evdev.ecodes.ABS_Y,flat=10,fuzz=20)
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_X)
        if math.fabs(absinfo.max) > math.fabs(absinfo.min) : max = math.fabs(absinfo.max)
        else : max = math.fabs(absinfo.max)
        self.motors_mx = 1200.0/math.fabs(max)
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_Y)
        if math.fabs(absinfo.max) > math.fabs(absinfo.min) : max = math.fabs(absinfo.max)
        else : max = math.fabs(absinfo.max)
        self.motors_my = 1200.0/math.fabs(max)
        self.rotation_speed = 300
        
# -----------------------------------

# -----------------------------------
async def event_loop(gamepad : Gamepad,
                     servos : Servos) -> bool:
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
        gamepad.gamepad.close()
        print("Finished event_loop")
        return True
# -----------------------------------

# -----------------------------------
def _update_servos(gamepad : Gamepad,
                   servos : Servos,
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
    while gamepad.control_motors :
        volts = motors.get_battery()
        print(f"Motor voltage: {volts}")
        await asyncio.sleep(2.0)
    print("Finished battery_loop")
    return True
#-----------------------------------

async def gamepad_control() :
    my_servos  = Servos()
    my_motors  = Motors()
    my_gamepad = Gamepad()

    loop   = asyncio.get_running_loop()
    future = await asyncio.gather(my_gamepad.event_loop(),
                                  my_gamepad.drive_loop(),
                                  my_gamepad.battery_loop())  
    
    my_servos.deinit()
    my_motors.deinit()

if __name__ == "__main__":
    asyncio.run(gamepad_control())




