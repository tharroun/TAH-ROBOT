import cv2
import time
from multiprocessing import JoinableQueue
import pprint
import numpy
import yaml
from picamera2 import Picamera2

small_kernel   = numpy.ones((3, 3), numpy.uint8)
medium_kernel  = numpy.ones((6, 6), numpy.uint8)
large_kernel   = numpy.ones((9, 9), numpy.uint8)

calbiration_filename = '/home/tah/GitHub/TAH-ROBOT/color_correction/calibration.yaml' 

class Camera:
    """
     Picamera module 3
    """
    def __init__(
        self, 
        log :    bool = False,
        logfile: str  = "PiCamMod3.conf"
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
        cv2.createTrackbar("LH", 'Camera', 60, 255, self.nothing)   # OpenCV hue max = 179
        cv2.createTrackbar("LS", 'Camera', 60, 255, self.nothing)
        cv2.createTrackbar("LV", 'Camera', 60, 255, self.nothing)
        cv2.createTrackbar("UH", 'Camera', 115, 255, self.nothing)
        cv2.createTrackbar("US", 'Camera', 255, 255, self.nothing)
        cv2.createTrackbar("UV", 'Camera', 255, 255, self.nothing)
        #cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty("Camera", cv2.WND_PROP_TOPMOST, 0)
        
        self.picam2.start()
# ------------------------------------------

    def nothing(self, s):
        return None

# ------------------------------------------
    def start(self):
        t1 = time.perf_counter() 
        while True:
            image  = self.picam2.capture_array()
            frame = cv2.resize(image,(596,324),interpolation = cv2.INTER_CUBIC)
            #frame = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)
            
            l_h = cv2.getTrackbarPos('LH','Camera')
            l_s = cv2.getTrackbarPos('LS','Camera')
            l_v = cv2.getTrackbarPos('LV','Camera')

            u_h = cv2.getTrackbarPos('UH','Camera')
            u_s = cv2.getTrackbarPos('US','Camera')
            u_v = cv2.getTrackbarPos('UV','Camera')

            l_b = numpy.array([l_h, l_s, l_v])
            u_b = numpy.array([u_h, u_s, u_v])

            frame_hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
            color_mask = cv2.inRange(frame_hsv, l_b, u_b)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, small_kernel, iterations = 1)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN,  small_kernel, iterations = 7)

            green_frame = cv2.bitwise_and(frame,frame,mask=color_mask)
            gray_frame = cv2.cvtColor(green_frame, cv2.COLOR_BGR2GRAY)

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

            
            cv2.imshow("Camera", frame)

            if cv2.waitKey(1)==ord('q'):
                data = {'hsv': {'min': [int(l_h),int(l_s),int(l_v)], 'max': [int(u_h),int(u_s),int(u_v)]}}
                with open(calbiration_filename,'w') as file:
                    yaml.dump(data,file)
                time.sleep(0.5)
                break
        cv2.destroyAllWindows()
# ------------------------------------------

# ------------------------------------------
    def deinit(self):
        self.picam2.stop()
        self.picam2.close()
# ------------------------------------------

if __name__ == "__main__":
    my_camera = Camera()
    my_camera.start()
    my_camera.deinit()

