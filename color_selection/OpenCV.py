import cv2
import time
import pprint
from picamera2 import Picamera2

picam2 = Picamera2()

with open("PiCamMod3.conf","w") as fp:
    pprint.pp(picam2.camera_controls,fp)
    pprint.pp(picam2.sensor_modes,fp)

mode   = picam2.sensor_modes[0]
config = picam2.create_preview_configuration(main={'size': (4608,2592),
                                                   'format': 'RGB888'})
picam2.align_configuration(config)
picam2.configure(config)

picam2.start()

t1 = time.time() 
while True:
    im= picam2.capture_array()
    res = cv2.resize(im,(1152,648),interpolation = cv2.INTER_CUBIC)
    cv2.imshow("Camera", res)
    t2 = time.time()
    #print(1/(t2-t1))
    t1 = t2
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()
picam2.stop()
picam2.close()

TFprTJJWBz9Scx4

