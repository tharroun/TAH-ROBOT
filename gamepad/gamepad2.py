#!/usr/bin/env python3
#coding=utf8
import evdev
import math
import sys
import asyncio
from   multiprocessing import JoinableQueue
sys.path.append('/home/tah/GitHub/TAH-ROBOT')


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
        # LINEAR MAPING OF STICK (0,ABS(MIN,MAX)) -> (0,1200) PWM SPEED UNITS
        #self.gamepad.set_absinfo(evdev.ecodes.ABS_X,flat=10,fuzz=20)
        #self.gamepad.set_absinfo(evdev.ecodes.ABS_Y,flat=10,fuzz=20)
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_X)
        if math.fabs(absinfo.max) > math.fabs(absinfo.min) : max = math.fabs(absinfo.max)
        else : max = math.fabs(absinfo.min)
        self.motors_mx = 1200.0/math.fabs(max)
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_Y)
        if math.fabs(absinfo.max) > math.fabs(absinfo.min) : max = math.fabs(absinfo.max)
        else : max = math.fabs(absinfo.min)
        self.motors_my = 1200.0/max
        self.rotation_speed = 300
        return
    
    def deinit(self):
        self.running = False
        self.gamepad.close()
        
# -----------------------------------

# -----------------------------------
async def event_loop(gamepad : Gamepad) -> bool:
    sx,sy=0,0
    async for event in gamepad.gamepad.async_read_loop() :
        if event.code == evdev.ecodes.BTN_MODE and event.value == 0:
            gamepad.running = False
            break

        if event.type ==  evdev.ecodes.EV_ABS :
            if event.code == evdev.ecodes.ABS_RY : 
                print("RY",event.value)
            if event.code == evdev.ecodes.ABS_RX : 
                print("RY",event.value)
        
    print("Finished event_loop")
    return True
# -----------------------------------

# -----------------------------------
async def gamepad_control() :
    my_gamepad = Gamepad()

    loop   = asyncio.get_running_loop()
    future = await asyncio.gather(event_loop(my_gamepad))  

    my_gamepad.deinit()
# -----------------------------------

if __name__ == "__main__":
    asyncio.run(gamepad_control())




