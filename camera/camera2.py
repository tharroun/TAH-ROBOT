import cv2
import time
import pprint
from   picamera2 import Picamera2
from   os.path import exists
import numpy
import yaml
import multiprocessing


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
    volts = "0.0 V"
    fps = "0.0 FPS"
    t1 = time.perf_counter() 
    while True:
        im  = my_camera.picam2.capture_array()
        #frame = cv2.resize(im,(596,324),interpolation = cv2.INTER_CUBIC)
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


if __name__ == "__main__":
    my_camera = Camera()
    view(my_camera)
    my_camera.deinit()

