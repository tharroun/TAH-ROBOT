import sys
import multiprocessing

sys.path.append('/home/tah/GitHub/TAH-ROBOT/camera')
from camera  import Camera

def robot_see(qs,qm,cap) -> int:
    
    return 0


if __name__ == "__main__":

    qs = multiprocessing.JoinableQueue() 
    qm = multiprocessing.JoinableQueue()

    thread_vision = multiprocessing.Process(target=robot_see, args=(qs,qm,cap))
    thread_vision.start()