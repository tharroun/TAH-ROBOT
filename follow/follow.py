import evdev
import math
import sys
import asyncio
import multiprocessing
import time
import cv2
import numpy
import yaml
import os.path 
import enum
from operator import itemgetter

sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos import Servos
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')
from motors import Motors
sys.path.append('/home/tah/GitHub/TAH-ROBOT/gamepad')
from gamepad import Gamepad
sys.path.append('/home/tah/GitHub/TAH-ROBOT/camera')
from camera import Camera
sys.path.append('/home/tah/GitHub/TAH-ROBOT/pid')
from pid  import MyPID

small_kernel   = numpy.ones((3, 3), numpy.uint8)
medium_kernel  = numpy.ones((6, 6), numpy.uint8)
large_kernel   = numpy.ones((9, 9), numpy.uint8)

class PROCESS_ACTION(enum.Enum):
    KILL_THREAD = 1
    LOST_OBJECT = 2

class FOLLOW_ACTION(enum.Flag):
    DRIVE  = enum.auto()
    SERVOS = enum.auto()
    MOTORS = enum.auto()


# -----------------------------------
async def event_loop(gamepad : Gamepad,
                     servos  : Servos):
    sx,sy=0,0
    async for event in gamepad.gamepad.async_read_loop() :
        if event.code == evdev.ecodes.KEY_MENU and event.value == 0:
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
        if rcw == 1023 and rccw == 0   : omega = gamepad.rotation_speed
        elif rcw == 0 and rccw == 1023 : omega = -gamepad.rotation_speed
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

# ------------------------------------------
def robot_see(battery_queue  : type[multiprocessing.JoinableQueue],
              tracking_queue : type[multiprocessing.JoinableQueue]):

    # ------
    calbiration_filename = '/home/tah/GitHub/TAH-ROBOT/color_correction/calibration.yaml' 
    if os.path.exists(calbiration_filename) == False:
        raise FileNotFoundError("calibration.yaml does nto exist.")
    with open(calbiration_filename,'r') as file:
        color_range = yaml.safe_load(file)
    COLOR_MIN = numpy.array(color_range['hsv']['min'],numpy.uint8)
    COLOR_MAX = numpy.array(color_range['hsv']['max'],numpy.uint8)
    # ------

    my_camera = Camera()

    tracking_queue.put((800,480))

    t1 = time.perf_counter() 
    volts = "0.0 V"
    while True:
        im  = my_camera.picam2.capture_array()
        frame = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)
        #-------------------------------
        frame_hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
        color_mask = cv2.inRange(frame_hsv, COLOR_MIN, COLOR_MAX)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, small_kernel, iterations = 1)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN,  small_kernel, iterations = 7)

        green_frame = cv2.bitwise_and(frame,frame,mask=color_mask)
        gray_frame = cv2.cvtColor(green_frame, cv2.COLOR_BGR2GRAY)
        #gray_frame = cv2.medianBlur(gray_frame, 7) #Doesn't seem to be needed.

        rows = gray_frame.shape[0]
        circles = cv2.HoughCircles(gray_frame, cv2.HOUGH_GRADIENT, 1, rows / 2,
                               param1=300, param2=12,
                               minRadius=5, maxRadius=150)
        
        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))
            # Assume only one circle found, mostly becuase I don't 
            # know how to sort the results.
            # circles = sorted(circles, key=itemgetter(1), reverse=True)
            #-------------------------------
            cv2.circle(frame, (circles[0][0][0], circles[0][0][1]), 
                       circles[0][0][2], (255, 0, 255), 3)    
            #-------------------------------
            t2 = time.perf_counter()
            dt = t2-t1
            fps = numpy.round(1/dt,1)
            t1 = t2
            cv2.putText(frame, str(fps)+" FPS", 
                        org = (40,100), 
                        fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale = 1, 
                        color = (255, 0, 0), 
                        thickness = 2, 
                        lineType = cv2.LINE_8)
            #-------------------------------
            tracking_queue.put((i[0],i[1],i[2],dt))
        else: 
            tracking_queue.put(PROCESS_ACTION.LOST_OBJECT)   
        #-------------------------------
        if battery_queue.empty() == False : 
            volts = battery_queue.get() 
            if volts is PROCESS_ACTION.KILL_THREAD: 
                break
        cv2.putText(frame, volts, 
                    org = (40,70), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 1, 
                    color = (255, 0, 0), 
                    thickness = 2, 
                    lineType = cv2.LINE_8)        
        #-------------------------------
        t = os.popen('vcgencmd measure_temp').readline().split('=')[1].rstrip()
        cv2.putText(frame, t, 
                    org = (40,40), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 1, 
                    color = (255, 0, 0), 
                    thickness = 2, 
                    lineType = cv2.LINE_8)
        #-------------------------------
        cv2.imshow("Camera", frame)
        # This time delay slows the fps and causes the RPi to run cooler!
        time.sleep(0.05)
        #-------------------------------
        if cv2.waitKey(1)==ord('q'):
            break
        #-------------------------------
    cv2.destroyAllWindows()
    my_camera.deinit()
    print("Finished robot_see")
    return

# ------------------------------------------


# -------------------------------------------
def robot_move(servos_instance : Servos,
               motors_instance : Motors,
               vision_queue : type[multiprocessing.JoinableQueue],
               follow_action: FOLLOW_ACTION):
    
    pidz = MyPID(40.0,0,0)
    pido = MyPID( 4.0,0,0)
    pidx = MyPID(0.01,0.000,0.002)
    pidy = MyPID(0.03,0.000,0.002)

    (width,height) = vision_queue.get()
    vision_queue.task_done()
    assert (width,height)==(800,480) , print("First data in servo queue is not the width/height.")
    cX = width/2.0
    cY = height/2.0
    
    while True:
        data = vision_queue.get()
        if data is PROCESS_ACTION.KILL_THREAD:
            motors_instance.stop()
            vision_queue.task_done()
            break
        elif data is PROCESS_ACTION.LOST_OBJECT:
            if (FOLLOW_ACTION.MOTORS in follow_action) : motors_instance.stop()
            pass
        else :
            #---------------------
            if (FOLLOW_ACTION.SERVOS in follow_action) :
                #---
                move_x = pidx.pid(cX, data[0], data[3])
                new_x = numpy.clip(servos_instance.servo0.angle + move_x, 1.0,179.0)
                servos_instance.servo0.angle = int(new_x)
                #---
                move_y = pidy.pid(cY, data[1], data[3])
                new_y = numpy.clip(servos_instance.servo1.angle - move_y, 1.0,179.0)
                servos_instance.servo1.angle = int(new_y)
                #---
            if (FOLLOW_ACTION.MOTORS in follow_action):
                if (FOLLOW_ACTION.SERVOS in follow_action):
                    #---
                    omega = 0
                    # object left and looking left 
                    if new_x < 30 and servos_instance.servo0.angle < 45 :
                        omega = -pido.pid(cX, data[0], data[3])
                    # object right and looking right 
                    if new_x > 150 and servos_instance.servo0.angle > 135 : 
                        omega = -pido.pid(cX, data[0], data[3])
                    #---
                    move_z = pidz.pid(40, data[2], data[3])
                    #---
                    motors_instance.go(move_z,0.0,omega)
                    #---
                else:
                    omega = -pido.pid(cX, data[0], data[3])
                    move_z = pidz.pid(40, data[2], data[3])
                    motors_instance.go(move_z,0.0,omega)
            #---------------------
        #------
        vision_queue.task_done()
    print("Finished robot_move")
    return
# -------------------------------------------


if __name__ == "__main__":
    
    # Accessing command-line arguments   
    arguments   = sys.argv       # List of arguments   
    script_name = sys.argv[0]  # Name of the script   
    if (len(sys.argv) != 2) :
        raise Exception("Please provide one argument (drive, servos, motors, both).") 
    if   (sys.argv[1].lower()=='drive') :
        follow_action = FOLLOW_ACTION.DRIVE
    elif   (sys.argv[1].lower()=='servos') :
        follow_action = FOLLOW_ACTION.SERVOS
    elif (sys.argv[1].lower()=='motors') :
        follow_action = FOLLOW_ACTION.MOTORS
    elif (sys.argv[1].lower()=='both') :
        follow_action = FOLLOW_ACTION.SERVOS | FOLLOW_ACTION.MOTORS
    else:
        raise Exception("Please provide one argument (servos, motors, both).")

    my_servos  = Servos()
    my_servos.servo0.angle = 90
    my_servos.servo1.angle = 90
    my_motors  = Motors()
    my_motors.stop()
    my_gamepad = Gamepad()

    battery_queue  = multiprocessing.JoinableQueue()
    tracking_queue = multiprocessing.JoinableQueue()
    
    gamepad_process = multiprocessing.Process(target=robot_control, args=(my_servos, my_motors, my_gamepad, battery_queue))
    gamepad_process.start()

    vision_process = multiprocessing.Process(target=robot_see, args=(battery_queue, tracking_queue))
    vision_process.start()

    move_process = multiprocessing.Process(target=robot_move, args=(my_servos, my_motors, tracking_queue, follow_action))
    move_process.start()

    gamepad_process.join()
    battery_queue.put(PROCESS_ACTION.KILL_THREAD)
    tracking_queue.put(PROCESS_ACTION.KILL_THREAD)
    vision_process.join()
    move_process.join()

    my_servos.servo0.angle = 90
    my_servos.servo1.angle = 90
    time.sleep(0.5)
    my_servos.deinit()
    my_motors.deinit()
    my_gamepad.deinit()





