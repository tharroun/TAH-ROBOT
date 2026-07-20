import evdev
import math
import sys
import asyncio
import multiprocessing
import time
import cv2
import numpy
import enum

sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos import Servos
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')
from motors import Motors
sys.path.append('/home/tah/GitHub/TAH-ROBOT/gamepad')
from gamepad import Gamepad
sys.path.append('/home/tah/GitHub/TAH-ROBOT/camera')
from camera import Camera

class PROCESS_ACTION(enum.Enum):
    KILL_THREAD = 1
    LOST_OBJECT = 2

# -----------------------------------
async def event_loop(gamepad : Gamepad,
                     servos  : Servos):
    sx,sy=0,0
    async for event in gamepad.gamepad.async_read_loop() :
        #if event.code == evdev.ecodes.BTN_MODE and event.value == 0: #USB 8Bitdo
        if event.code == evdev.ecodes.KEY_MENU and event.value == 0:  #Bluetooth 8Bitdo X+start
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
                if gamepad.rotation_speed > 1200 : gamepad.rotation_speed = 1200
                if gamepad.rotation_speed < 0   : gamepad.rotation_speed = 0
        
    print("Finished event_loop")
    return
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
                     motors : Motors):
    omega = 0
    while gamepad.running :
        mx = gamepad.gamepad.absinfo(evdev.ecodes.ABS_X).value
        my = gamepad.gamepad.absinfo(evdev.ecodes.ABS_Y).value
            
        rcw  = gamepad.gamepad.absinfo(evdev.ecodes.ABS_RZ).value
        rccw = gamepad.gamepad.absinfo(evdev.ecodes.ABS_Z).value
        if rcw == 1023 and rccw == 0   : omega = -gamepad.rotation_speed
        elif rcw == 0 and rccw == 1023 : omega = gamepad.rotation_speed
        else : omega = 0

        speed_x = gamepad.motors_mx*math.fabs(mx)+gamepad.motors_bx
        speed_y = gamepad.motors_my*math.fabs(my)+gamepad.motors_by
        speed = math.sqrt(speed_x*speed_x+speed_y*speed_y)
        direction = math.atan2(mx-gamepad.motors_hx,my-gamepad.motors_hy)*180.0/math.pi+180.0
        motors.go(speed,direction,omega)
        await asyncio.sleep(0.1)
    motors.stop()
    print("Finished drive_loop")
    return
# -----------------------------------


# -----------------------------------
async def battery_loop(gamepad       : Gamepad,
                       motors        : Motors,
                       battery_queue : type[multiprocessing.JoinableQueue]):
    while gamepad.running :
        volts = motors.get_battery()
        battery_queue.put(volts) # type: ignore
        await asyncio.sleep(2.0)
    print("Finished battery_loop")
    return
#-----------------------------------

#-----------------------------------
async def gamepad_main_loop(my_servos     : Servos,
                            my_motors     : Motors,
                            my_gamepad    : Gamepad,
                            battery_queue : type[multiprocessing.JoinableQueue]):
    loop   = asyncio.get_running_loop()
    future = await asyncio.gather(event_loop(my_gamepad,my_servos),
                                  drive_loop(my_gamepad,my_motors),
                                  battery_loop(my_gamepad,my_motors,battery_queue))
    print("Finished gamepad_main_loop")
    return
#-----------------------------------

#-----------------------------------
def robot_control(my_servos     : Servos,
                  my_motors     : Motors,
                  my_gamepad    : Gamepad,
                  battery_queue : type[multiprocessing.JoinableQueue]) :
    asyncio.run(gamepad_main_loop(my_servos,my_motors,my_gamepad,battery_queue))
    print("Finished robot_control")
    return
#-----------------------------------

# -------------------------------------------
def robot_see(battery_queue : type[multiprocessing.JoinableQueue]):
    
    my_camera = Camera()

    # ------------------------------------------
    volts = "0.0 V"
    fps   = "0.0 FPS"
    t1    = time.perf_counter() 
    while True:
        im  = my_camera.picam2.capture_array()
        #frame = cv2.resize(im,(596,324),interpolation = cv2.INTER_CUBIC)
        frame = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)
        #-------------------------------
        if battery_queue.empty() == False :
            volts = battery_queue.get() 
            if volts is PROCESS_ACTION.KILL_THREAD: 
                break
        cv2.putText(frame, volts, 
                    org = (40,40), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 1, 
                    color = (255, 0, 0), 
                    thickness = 2, 
                    lineType = cv2.LINE_8)
        #-------------------------------
        t2  = time.perf_counter()
        fps = numpy.round(1/(t2-t1),1)
        t1  = t2
        cv2.putText(frame, str(fps)+" FPS", 
                    org = (40,70), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 1, 
                    color = (255, 0, 0), 
                    thickness = 2, 
                    lineType = cv2.LINE_8)
        #-------------------------------
        cv2.imshow("Camera", frame)
        #-------------------------------
        if cv2.waitKey(1)==ord('q'):
            break
        #-------------------------------
    cv2.destroyAllWindows()
    # ------------------------------------------

    my_camera.deinit()
    return
# -------------------------------------------



if __name__ == "__main__":
    
    my_servos  = Servos()
    my_servos.servo0.angle = 90
    my_servos.servo1.angle = 90
    my_motors  = Motors()
    my_motors.stop()
    my_gamepad = Gamepad()

    battery_queue = multiprocessing.JoinableQueue()
    
    vision_process = multiprocessing.Process(target=robot_see, args=(battery_queue,))
    vision_process.start()

    gamepad_process = multiprocessing.Process(target=robot_control, args=(my_servos,my_motors,my_gamepad,battery_queue))
    gamepad_process.start()

    gamepad_process.join()
    battery_queue.put(PROCESS_ACTION.KILL_THREAD)
    vision_process.join()

    my_servos.servo0.angle = 90
    my_servos.servo1.angle = 90
    my_servos.deinit()
    my_motors.deinit()
    my_gamepad.deinit()





