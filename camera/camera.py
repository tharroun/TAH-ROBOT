import sys
import cv2
import time
import pprint
import yaml
import os.path 
from   picamera2 import Picamera2
import numpy

sys.path.append('/home/tah/GitHub/TAH-ROBOT')

small_kernel   = numpy.ones((3, 3), numpy.uint8)
medium_kernel  = numpy.ones((6, 6), numpy.uint8)
large_kernel   = numpy.ones((9, 9), numpy.uint8)

class Camera:
    """
     Picamera module 3
    """
    def __init__(
        self, 
        log : bool = False,
        logfile: str = "PiCamMod3.conf"
    ):
        #Picamera2.set_logging(Picamera2.ERROR)
        self.picam2 = Picamera2()

        if log:
            with open(logfile,"w") as fp:
                pprint.pp(self.picam2.camera_controls,fp)
                pprint.pp(self.picam2.sensor_modes,fp)

        mode   = self.picam2.sensor_modes[0]
        config = self.picam2.create_preview_configuration(main={'size': (2304,1296),
                                                                'format': 'RGB888'})
        self.picam2.align_configuration(config)
        self.picam2.configure(config)

        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #cv2.setWindowProperty("Camera", cv2.WND_PROP_TOPMOST, 0)
        
        self.picam2.start()
# ------------------------------------------
# ------------------------------------------
    def deinit(self):
        self.picam2.stop()
        self.picam2.close()
# ------------------------------------------


# ------------------------------------------
def view(my_camera : Camera):

    fps = "0.0 FPS"
    t1 = time.perf_counter() 
    while True:
        im  = my_camera.picam2.capture_array()
        frame = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)
        #-------------------------------
        t2 = time.perf_counter()
        fps = numpy.round(1/(t2-t1),1)
        t1 = t2
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

# ------------------------------------------
def follow(my_camera : Camera):
    # ------
    calbiration_filename = '/home/tah/GitHub/TAH-ROBOT/color_correction/calibration.yaml' 
    if os.path.exists(calbiration_filename) == False:
        raise FileNotFoundError("calibration.yaml does nto exist.")
    with open(calbiration_filename,'r') as file:
        color_range = yaml.safe_load(file)
    COLOR_MIN = numpy.array(color_range['hsv']['min'],numpy.uint8)
    COLOR_MAX = numpy.array(color_range['hsv']['max'],numpy.uint8)
    # ------

    fps = "0.0 FPS"
    t1 = time.perf_counter() 
    while True:
        im  = my_camera.picam2.capture_array()
        #frame = cv2.resize(im,(596,324),interpolation = cv2.INTER_CUBIC)
        frame = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)
        #-------------------------------
        frame_hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
        color_mask = cv2.inRange(frame_hsv, COLOR_MIN, COLOR_MAX)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, small_kernel, iterations = 1)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN,  small_kernel, iterations = 7)

        green_frame = cv2.bitwise_and(frame,frame,mask=color_mask)
        gray_frame = cv2.cvtColor(green_frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.medianBlur(gray_frame, 7)

        rows = gray_frame.shape[0]
        circles = cv2.HoughCircles(gray_frame, cv2.HOUGH_GRADIENT, 1, rows / 2,
                               param1=300, param2=12,
                               minRadius=5, maxRadius=150)
        
        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))
            for i in circles[0, :]:
                cv2.circle(frame, (i[0], i[1]), i[2], (255, 0, 255), 3)
        #-------------------------------
        t2 = time.perf_counter()
        fps = numpy.round(1/(t2-t1),1)
        t1 = t2
        cv2.putText(frame, str(fps)+" FPS", 
                    org = (40,70), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 1, 
                    color = (255, 0, 0), 
                    thickness = 2, 
                    lineType = cv2.LINE_8)
        #-------------------------------
        t = os.popen('vcgencmd measure_temp').readline().split('=')[1].rstrip()
        cv2.putText(frame, t, 
                    org = (40,100), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale = 1, 
                    color = (255, 0, 0), 
                    thickness = 2, 
                    lineType = cv2.LINE_8)
        #-------------------------------
        cv2.imshow("Camera", frame)
        time.sleep(0.1)
            #-------------------------------
        if cv2.waitKey(1)==ord('q'):
            break
            #-------------------------------
    cv2.destroyAllWindows()
# ------------------------------------------


if __name__ == "__main__":
    my_camera = Camera()
    follow(my_camera)
    my_camera.deinit()

