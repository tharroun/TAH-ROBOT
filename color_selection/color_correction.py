import cv2
import time
from multiprocessing import JoinableQueue
import pprint
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
        cv2.createTrackbar("LH", 'Camera', 0, 255, nothing)   # OpenCV hue max = 179
        cv2.createTrackbar("LS", 'Camera', 0, 255, nothing)
        cv2.createTrackbar("LV", 'Camera', 0, 255, nothing)
        cv2.createTrackbar("UH", 'Camera', 255, 255, nothing)
        cv2.createTrackbar("US", 'Camera', 255, 255, nothing)
        cv2.createTrackbar("UV", 'Camera', 255, 255, nothing)
        #cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty("Camera", cv2.WND_PROP_TOPMOST, 0)
        
        self.picam2.start()
# ------------------------------------------

# ------------------------------------------
    def start(self):
        t1 = time.perf_counter() 
        while True:
            im  = self.picam2.capture_array()
            res = cv2.resize(im,(596,324),interpolation = cv2.INTER_CUBIC)
            #res = cv2.resize(im,(800,480),interpolation = cv2.INTER_CUBIC)

            t2 = time.perf_counter()
            #print(1/(t2-t1))
            t1 = t2
            
            l_h = cv2.getTrackbarPos('LH','config')
            l_s = cv2.getTrackbarPos('LS','config')
            l_v = cv2.getTrackbarPos('LV','config')

            u_h = cv2.getTrackbarPos('UH','config')
            u_s = cv2.getTrackbarPos('US','config')
            u_v = cv2.getTrackbarPos('UV','config')

            l_b = np.array([l_h, l_s, l_v])
            u_b = np.array([u_h, u_s, u_v])

            res_hsv  = cv2.cvtColor(res, cv2.COLOR_BGR2HSV_FULL)
            color_mask = cv2.inRange(res_hsv, l_b, u_b)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, small_kernel, iterations = 1)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, small_kernel,iterations = 1)

            cv2.imshow("Camera", color_mask)

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

