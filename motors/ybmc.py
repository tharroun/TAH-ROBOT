import logging
import struct
import time
import serial
import threading
from typing import List, Tuple
import collections
from enum import Enum

class EncoderMode(Enum):
    NOTHING  = 0
    TOTAL    = 1
    REALTIME = 2
    SPEED    = 3


class YBMC:
    """
    The Yahboom 4-Channel Motor Controller
    """
# -----------------------------------
    def __init__(
        self, device: str = "/dev/ttyUSB0", 
        enable_recv: bool = True,
        logfile: str = "YBMC.log"
    ):

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)

        try:
            self.port = serial.Serial(None)
            self.port.rts      = False
            self.port.dts      = False      
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
        self.set_motor_deadzone(1800)
        self.set_pulse_phase(30)
        self.set_pulse_line(11)
        self.set_wheel_diam(95)
        self.send_data("$upload:0,0,0#")
        self.control_pwm(0,0,0,0)
        self.send_upload_command(EncoderMode.NOTHING)
        self.send_data("$read_flash#")
        self.logger.info("Initialized motor parameters.")
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
Some data follow the format $DATA#, but many do not.
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

if __name__ == "__main__":

    ybmc = YBMC()
    ybmc.get_battery()

    ybmc.control_pwm(100, 100, 100, 100)
    time.sleep(2)
    ybmc.send_upload_command(EncoderMode.SPEED)
    time.sleep(2)
    ybmc.control_pwm(0, 0, 0, 0)
    time.sleep(0.5)

    ybmc.stopYBMC()
