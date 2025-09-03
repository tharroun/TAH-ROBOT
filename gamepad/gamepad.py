#!/usr/bin/env python3
#coding=utf8
import evdev
import math
import sys
import asyncio
import pprint
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
        servos_instance : Servos | None = None,
        motors_instance : Motors | None = None,
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

        # - SERVOS -----
        self.control_servos = True
        if servos_instance != None : 
            self.servos = servos_instance
        else : 
            raise RuntimeError(f"Must supply a valid servo instance, or set control_servos to False.")
        self.servos.servo0.angle = 90
        self.servos.servo1.angle = 90
        # RIGHT STICK
        # LINEAR MAPING OF STICK (MIN,MAX) -> (0,180) PWM VALUES
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RX)
        self.servos_mx = 180.0/math.fabs(absinfo.max-absinfo.min)
        self.servos_bx = -self.servos_mx*absinfo.min
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RY)
        self.servos_my = 153.0/math.fabs(absinfo.max-absinfo.min)
        self.servos_by = -self.servos_my*absinfo.min
        
        # - MOTORS -----
        self.control_motors = True
        if motors_instance != None :
            self.motors = motors_instance
        else :
            raise RuntimeError(f"Must supply a valid motors instance, or set control_motors to False.")
        # LEFT STICK
        # LINEAR MAPING OF STICK ABS(MIN,MAX) -> (0,1500) PWM SPEED UNITS
        self.gamepad.set_absinfo(evdev.ecodes.ABS_X,flat=10,fuzz=20)
        self.gamepad.set_absinfo(evdev.ecodes.ABS_Y,flat=10,fuzz=20)
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
    async def run_00(self):
        sx=0
        sy=0
        async for event in self.gamepad.async_read_loop() :
            if event.code == evdev.ecodes.BTN_MODE and event.value == 0:
                self.control_motors = False
                break
            # Left joystick controls the motors
            # We have a linar mapping of speed, we need to find the direction.
            # Right joytick controls the servos.
            if event.type ==  evdev.ecodes.EV_ABS :
                if event.code == evdev.ecodes.ABS_RY : 
                    sy=event.value
                    self._update_servos(sx,sy)
                if event.code == evdev.ecodes.ABS_RX : 
                    sx=event.value
                    self._update_servos(sx,sy)
                if event.code == evdev.ecodes.ABS_HAT0Y :
                    if event.value ==  1 : self.rotation_speed -= 50
                    if event.value == -1 : self.rotation_speed += 50
                if self.rotation_speed > 900 : self.rotation_speed = 900
                if self.rotation_speed < 0   : self.rotation_speed = 0
        return
# -----------------------------------

# -----------------------------------
    def _update_servos(self,
                       sx: float = 0,
                       sy: float= 0) :
        deg_x = math.trunc(self.servos_mx*sx+self.servos_bx)
        deg_y = math.trunc(self.servos_my*sy+self.servos_by)
        #print(deg_x,deg_y)
        self.servos.servo0.angle = deg_x
        self.servos.servo1.angle = deg_y
        return
# -----------------------------------

# -----------------------------------
    async def run_01(self):
        omega = 0
        while self.control_motors :
            mx = self.gamepad.absinfo(evdev.ecodes.ABS_X).value
            my = self.gamepad.absinfo(evdev.ecodes.ABS_Y).value
            
            rcw  = self.gamepad.absinfo(evdev.ecodes.ABS_RZ).value
            rccw = self.gamepad.absinfo(evdev.ecodes.ABS_Z).value
            if rcw == 255 and rccw == 0   : omega = self.rotation_speed
            elif rcw == 0 and rccw == 255 : omega = -self.rotation_speed
            else : omega = 0

            speed_x = self.motors_mx*math.fabs(mx)
            speed_y = self.motors_my*math.fabs(my)
            speed = math.sqrt(speed_x*speed_x+speed_y*speed_y)
            direction = math.atan2(mx,my)*180.0/math.pi + 180.0
            self.motors.go(speed,direction,omega)
            await asyncio.sleep(0.1)
        self.motors.stop()
        return
# -----------------------------------

async def gamepad_control() :
    my_servos  = Servos()
    my_motors  = Motors()
    my_gamepad = Gamepad(servos_instance=my_servos, motors_instance=my_motors)
    L = await asyncio.gather(
        my_gamepad.run_00(),
        my_gamepad.run_01())
    my_servos.deinit()
    my_motors.deinit()

if __name__ == "__main__":
    asyncio.run(gamepad_control())