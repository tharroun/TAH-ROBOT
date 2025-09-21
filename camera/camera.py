import cv2
import time
from   multiprocessing import JoinableQueue
import pprint
from   picamera2 import Picamera2
from   os.path import exists
import numpy
import yaml

small_kernel   = numpy.ones((3, 3), numpy.uint8)
medium_kernel  = numpy.ones((6, 6), numpy.uint8)
large_kernel   = numpy.ones((9, 9), numpy.uint8)

class Camera:
    """
     Picamera module 3
    """
    def __init__(
        self, 
        battery_queue  : type[JoinableQueue] | None = None,
        tracking_queue : type[JoinableQueue] | None = None,
        log : bool = False,
        logfile: str = "PiCamMod3.conf"
    ):
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
        #cv2.setWindowProperty("Camera", cv2.WND_PROP_TOPMOST, 0)e
        
        self.battery_message = False
        if battery_queue != None:
            self.battery_queue   = battery_queue
            self.battery_message = True
        
        self.tracking_object = False
        if tracking_queue != None:
            self.tracking_queue  = tracking_queue
            self.tracking_object = True
        
        self.picam2.start()
# ------------------------------------------

# ------------------------------------------
    def view(self):
        volts = "0.0 V"
        fps = "0.0 FPS"
        t1 = time.perf_counter() 
        while True:
            im  = self.picam2.capture_array()
            #frame = cv2.resize(im,(596,324),interpolation = cv2.INTER_CUBIC)
            frame = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)
            #-------------------------------
            if self.battery_message:
                if self.battery_queue.empty() == False : # type: ignore
                    volts = self.battery_queue.get() # type: ignore
            cv2.putText(frame, volts, 
                        org = (40,40), 
                        fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale = 1, 
                        color = (255, 0, 0), 
                        thickness = 2, 
                        lineType = cv2.LINE_8)
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
    def track(self):
        # ------
        calbiration_filename = '/home/tah/GitHub/TAH-ROBOT/color_correction/calibration.yaml' 
        if exists(calbiration_filename) == False:
            raise FileNotFoundError("calibration.yaml does nto exist.")
        with open(calbiration_filename,'r') as file:
            color_range = yaml.safe_load(file)
        COLOR_MIN = numpy.array(color_range['hsv']['min'],numpy.uint8)
        COLOR_MAX = numpy.array(color_range['hsv']['max'],numpy.uint8)
        # ------

        if self.tracking_object:
            #self.tracking_queue.put((596,324))
            self.tracking_queue.put((800,480))

        t1 = time.perf_counter() 
        volts = "0.0 V"
        while True:
            im  = self.picam2.capture_array()
            #frame = cv2.resize(im,(596,324),interpolation = cv2.INTER_CUBIC)
            frame = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)
            #-------------------------------
            frame_hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
            color_mask = cv2.inRange(frame_hsv, COLOR_MIN, COLOR_MAX)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, small_kernel, iterations = 1)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN,  small_kernel, iterations = 1)
            #-------------------------------
            contours,hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            if (contours):
                if (len(contours)>1) : 
                    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
                # ------------------------------------------------
                # area = cv2.contourArea(contours[0])
                # arclength = cv2.arcLength(contours[0],True)
                # circularity = 4*numpy.pi*area/(arclength*arclength)
                # NEXT TIME:https://docs.opencv.org/4.11.0/d4/d70/tutorial_hough_circle.html
                # ------------------------------------------------
                M = cv2.moments(contours[0])
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                radius = int(numpy.sqrt(M['m00']/numpy.pi))
                if radius > 10:
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
                    cv2.drawContours(frame,contours,0,(0,0,255),5)
                    if self.tracking_object:
                        self.tracking_queue.put((cx,cy,radius,fps))
            #-------------------------------
            if self.battery_message:
                if self.battery_queue.empty() == False :
                    volts = self.battery_queue.get()
            cv2.putText(frame, volts, 
                        org = (40,40), 
                        fontFace = cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale = 1, 
                        color = (255, 0, 0), 
                        thickness = 2, 
                        lineType = cv2.LINE_8)            
            #-------------------------------
            #cv2.imshow("Camera", frame)
            #-------------------------------
            if cv2.waitKey(1)==ord('q'):
                break
            #-------------------------------
        cv2.destroyAllWindows()
# ------------------------------------------


# ------------------------------------------
    def deinit(self):
        self.picam2.stop()
        self.picam2.close()
# ------------------------------------------

if __name__ == "__main__":
    my_camera = Camera()
    my_camera.track()
    my_camera.deinit()

