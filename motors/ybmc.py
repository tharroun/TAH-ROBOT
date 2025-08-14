#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/tah/Github/TAH-ROBOT')
import logging
import time
import serial
import threading
import math
from   enum import Enum
from   enum import IntEnum


class EncoderMode(IntEnum):
    NOTHING  = 0
    TOTAL    = 1
    REALTIME = 2
    SPEED    = 3

class Robot(IntEnum):
    WIDTH  = 476 # mm
    LENGTH = 334 # mm
    WHEEL_DIAMETER = 97 #mm

class YBMC:
    """
    The Yahboom 4-Channel Motor Controller
    """
# -----------------------------------
    def __init__(
        self, 
        device: str = "/dev/ttyUSB0", 
        enable_recv: bool = True,
        logfile: str = "YBMC.log"
    ):

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)

        try:
            self.port = serial.Serial(None)
            self.port.rts      = False
            self.port.dtr      = False      
            self.port.baudrate = 115200
            self.port.timeout  = 5
            self.port.stopbits = serial.STOPBITS_ONE
            self.port.bytesize = serial.EIGHTBITS
            self.port.setPort(device)
            self.port.open()
            time.sleep(0.1)
            self.logger.info("Opened serial port.")
        except serial.SerialException as e:
            raise RuntimeError(f"Failed to initialize serial port: {e}")
    
        self.enable_recv = enable_recv
        if enable_recv:
            self.stop_listening = False
            self.listening      = threading.Thread(target=self._listen_thread, daemon=False)
            self.listening.start()
            self.recv_buffer    = ""
            self.logger.info("Started listening to serial port.")

        self.set_motor_type(1)
        self.set_motor_deadzone(1500)
        self.set_pulse_phase(30)
        self.set_pulse_line(11)
        self.set_wheel_diam(95)
        self.send_data("$upload:0,0,0#")
        self.control_pwm(0,0,0,0)
        self.send_upload_command(EncoderMode.NOTHING)
        self.send_data("$read_flash#")
        self.logger.info("Initialized motor parameters.")

        self.W = Robot.WIDTH//2
        self.L = Robot.LENGTH//2
        self.wheel_diameter = Robot.WHEEL_DIAMETER
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0
        return
# -----------------------------------

# -----------------------------------

# -----------------------------------
    def _listen_thread(self):
        """
This is the Thread function target that listens for messages on the 
serial port. However it has a major problem using this interface to read 
the encoder data.

Using USART over USB:
1. The format of the return data is inconsistant. 
Some data follow the format '$DATA#', but many do not.
2. Turing on the encoder data means it is continuously transmitted, 
and the docs say at 10ms intervals. The data does follow the $DATA# format.
However, there is no way to time this correctly. As a result, using a 5 to 10ms
delay between serial reads may cut off the end of the data string, and using 20 to 60ms
delays may record two data strings in one.

The Yahboom method is to use longer delays between reads, and then
try and split the data if it was doubled up, and report the most recent.

I am using a 10ms delay, and accepting the closing of the data string (a '#')
may sometimes be missing, or in the next read. The idea is to then look for '$M' 
which is unique to the encoder data. 

All other data is shunted to log.
        """
        while not self.stop_listening:
            if self.port.in_waiting > 0:
                self.recv_buffer = self.port.read(self.port.in_waiting).decode().rstrip()
                if '$M' in self.recv_buffer:
                    print(self.recv_buffer)
                else:
                    self.logger.info(self.recv_buffer)
            else:
                time.sleep(0.01)
        return
# -----------------------------------

# -----------------------------------
    def stopYBMC(self):
        self.send_upload_command(EncoderMode.NOTHING)
        if self.enable_recv:
            self.stop_listening = True
            self.enable_recv    = False
            self.listening.join()
            self.logger.info("Stopped listening thread.")
        else: 
            self.logger.warning(f"Reception was not enabled to stop the listening thread.")
        self.port.close()
        self.logger.info("Closed serial port.")
        return
# -----------------------------------

# -----------------------------------
    def send_data(self, data: str):
        #print(data)
        self.port.write(data.encode())  
        self.port.flush()
        time.sleep(0.1)
        return
# -----------------------------------

# -----------------------------------
    def set_motor_type(self, mtype: int=1):
        self.send_data("$mtype:{}#".format(mtype))
        return
# -----------------------------------

# -----------------------------------
    def set_motor_deadzone(self, dz: int=1500):
        self.send_data("$deadzone:{}#".format(dz))
        return
# -----------------------------------

# -----------------------------------
    def set_pulse_line(self, pl: int=11):
        self.send_data("$mline:{}#".format(pl))
        return
# -----------------------------------

# -----------------------------------
    def set_pulse_phase(self, pp: int=30):
        self.send_data("$mphase:{}#".format(pp))
        return
# -----------------------------------

# -----------------------------------
    def set_wheel_diam(self, wheel: int=67):
        self.send_data("$wdiameter:{}#".format(wheel))
        return
# -----------------------------------

# -----------------------------------
    def get_battery(self):
        self.send_data("$read_vol#")
        return
# -----------------------------------

# -----------------------------------
    def send_upload_command(self, mode: int=0):
        if mode == EncoderMode.NOTHING:
            self.send_data("$upload:0,0,0#")
        elif mode == EncoderMode.TOTAL:
            self.send_data("$upload:1,0,0#")
        elif mode == EncoderMode.REALTIME:
            self.send_data("$upload:0,1,0#")
        elif mode == EncoderMode.SPEED:
            self.send_data("$upload:0,0,1#")
# -----------------------------------

# -----------------------------------
    def control_pwm(self, m1: int=0, m2: int=0, m3: int=0, m4: int=0):
        self.send_data("$pwm:{},{},{},{}#".format(m1, m2, m3, m4))
        return
# -----------------------------------

# -----------------------------------
    def set_velocity(self, 
                     velocity: float=0, 
                     direction: float=90.0, 
                     angular_rate: float=0):
        """
        Use polar coordinates to control moving
        motor1 v1|  ↑  |v2 motor3
                 |     |
        motor3 v2|     |v4 motor4
        :param velocity: mm/s
        :param direction: Moving direction 0~360deg, 90deg<--- ↑ ---> 270deg
        :param angular_rate:  The speed at which the chassis rotates
        :return:
        """
        rad_per_deg = math.pi / 180.0
        vx = velocity * math.cos(direction * rad_per_deg)
        vy = velocity * math.sin(direction * rad_per_deg)
        vp = -angular_rate # * (self.W + self.L)
        v1 = int(vx - vy - vp)
        v2 = int(vx + vy - vp)
        v3 = int(vx + vy + vp)
        v4 = int(vx - vy + vp)
        self.control_pwm(v2, -v4, -v1, v3)
        self.velocity     = velocity
        self.direction    = direction
        self.angular_rate = angular_rate
        return
# -----------------------------------
# -----------------------------------

if __name__ == "__main__":

    ybmc = YBMC()
    ybmc.get_battery()

    
    #ybmc.control_pwm(0, 0, 0, 500) #rotate cw
    #time.sleep(2)
    #ybmc.control_pwm(0, 0, 0, 0)

    
    ybmc.send_upload_command(EncoderMode.SPEED)
    ybmc.set_velocity(350.0, 0.0, 0.0)
    time.sleep(2)
    ybmc.set_velocity(850.0, 180.0, 0.0)
    time.sleep(2)
    ybmc.set_velocity(0.0, 0.0, 300)
    time.sleep(2)
    ybmc.set_velocity(0.0, 0.0, -800)
    time.sleep(2)
    ybmc.control_pwm(0, 0, 0, 0)
    time.sleep(0.5)
    
    ybmc.stopYBMC()
