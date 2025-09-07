import cv2
import time
from multiprocessing import JoinableQueue
import pprint
import numpy
from picamera2 import Picamera2

small_kernel   = numpy.ones((3, 3), numpy.uint8)
medium_kernel  = numpy.ones((6, 6), numpy.uint8)
large_kernel   = numpy.ones((9, 9), numpy.uint8)


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
        cv2.createTrackbar("LH", 'Camera', 0, 255, self.nothing)   # OpenCV hue max = 179
        cv2.createTrackbar("LS", 'Camera', 0, 255, self.nothing)
        cv2.createTrackbar("LV", 'Camera', 0, 255, self.nothing)
        cv2.createTrackbar("UH", 'Camera', 255, 255, self.nothing)
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
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, small_kernel,iterations = 1)

            contours,hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            if (contours):
                t2 = time.perf_counter()
                if (len(contours)>1) : 
                    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
                # ------------------------------------------------
                #area = cv2.contourArea(contours[0])
                #arclength = cv2.arcLength(contours[0],True)
                #circularity = 4*numpy.pi*area/(arclength*arclength)
                # NEXT TIME:https://docs.opencv.org/4.11.0/d4/d70/tutorial_hough_circle.html
                # ------------------------------------------------
                M = cv2.moments(contours[0])
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                radius = int(numpy.sqrt(M['m00']/numpy.pi))
                if radius > 10:
                    cv2.drawContours(frame,contours,0,(0,0,255),5)
                t1 = t2
            cv2.imshow("Camera", frame)

            if cv2.waitKey(1)==ord('q'):
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

