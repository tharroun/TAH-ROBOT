import cv2
import time
import pprint
from picamera2 import Picamera2


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
            with open("PiCamMod3.conf","w") as fp:
                pprint.pp(self.picam2.camera_controls,fp)
                pprint.pp(self.picam2.sensor_modes,fp)

        mode   = self.picam2.sensor_modes[0]
        config = self.picam2.create_preview_configuration(main={'size': (2304,1296),
                                                     'format': 'RGB888'})
        self.picam2.align_configuration(config)
        self.picam2.configure(config)

        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
        #cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty("Camera", cv2.WND_PROP_TOPMOST, 0)

        self.picam2.start()
# ------------------------------------------

# ------------------------------------------
    def start(self):
        t1 = time.time() 
        while True:
            im  = self.picam2.capture_array()
            res = cv2.resize(im,(596,324),interpolation = cv2.INTER_CUBIC)
            cv2.imshow("Camera", res)
            t2 = time.time()
            #print(1/(t2-t1))
            t1 = t2
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

