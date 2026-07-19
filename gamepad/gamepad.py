import evdev
import math
import sys
import asyncio
from   multiprocessing import JoinableQueue
import pprint
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
            if '8Bitdo'in device.name:  # Bluetooth BBitdo
            #if 'X-Box' in device.name: # USB 8Bitdo default
                found_gamepad = True
                break
        if found_gamepad: 
            self.gamepad = evdev.InputDevice(device.path) # type: ignore
        else :
            raise RuntimeError(f"Failed to initialize gamepad.")
        gamepad_str = pprint.pformat(self.gamepad.capabilities(verbose=True))
        print(gamepad_str)

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
        # LINEAR MAPING OF STICK (MIN,MAX) -> (-1200,1200) PWM SPEED UNITS
        #self.gamepad.set_absinfo(evdev.ecodes.ABS_X,flat=10,fuzz=20)
        #self.gamepad.set_absinfo(evdev.ecodes.ABS_Y,flat=10,fuzz=20)
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_X)
        #if math.fabs(absinfo.max) > math.fabs(absinfo.min) : max = math.fabs(absinfo.max)
        #else : max = math.fabs(absinfo.min)
        #self.motors_mx = 1200.0/math.fabs(max)
        self.motors_mx = (2*1200)/(absinfo.max-absinfo.min)
        self.motors_bx = (-1200) - (self.motors_mx*absinfo.min)
        self.motors_hx = (absinfo.max-absinfo.min)/2.0
        
        absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_Y)
        #if math.fabs(absinfo.max) > math.fabs(absinfo.min) : max = math.fabs(absinfo.max)
        #else : max = math.fabs(absinfo.min)
        #self.motors_my = 1200.0/math.fabs(max)
        self.motors_my = (2*1200)/(absinfo.max-absinfo.min)
        self.motors_by = (-1200) - (self.motors_mx*absinfo.min)
        self.motors_hy = (absinfo.max-absinfo.min)/2.0

        self.rotation_speed = 900
        return
    
    def deinit(self):
        self.running = False
        self.gamepad.close()
# -----------------------------------

running = True

# -----------------------------------
async def listen_00(dev : Gamepad):
    global running
    async for ev in dev.gamepad.async_read_loop():
        print("00:",evdev.categorize(ev),ev.value)
        if ev.code == evdev.ecodes.KEY_MENU and ev.value == 0:
            running = False
            break

# -----------------------------------
async def listen_01(dev : Gamepad):
    global running
    while running:
        mx = dev.gamepad.absinfo(evdev.ecodes.ABS_X).value
        my = dev.gamepad.absinfo(evdev.ecodes.ABS_Y).value
        speed_x = dev.motors_mx*math.fabs(mx)+dev.motors_bx
        speed_y = dev.motors_my*math.fabs(my)+dev.motors_by
        print("01:",mx,",",my,",",speed_x,",",speed_y)
        await asyncio.sleep(1.0)

# -----------------------------------
async def gamepad_control() :
    my_gamepad = Gamepad()

    loop   = asyncio.get_running_loop()
    future = await asyncio.gather(listen_00(my_gamepad),
                                  listen_01(my_gamepad))  

    my_gamepad.deinit()
# -----------------------------------

if __name__ == "__main__":
    asyncio.run(gamepad_control())




