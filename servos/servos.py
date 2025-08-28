#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
import time
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

class Servos:
    """
     A PCA9685 16-channel servo conrroller
    """
    def __init__(
        self, 
        channel_0: int = 0, 
        channel_1: int = 1, 
        logfile: str = "servos.log"
    ):

        # uses board.SCL and board.SDA
        self.i2c = board.I2C()  

        #pca = PCA9685(i2c, reference_clock_speed=25600000)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50
        self.servo0 = servo.Servo(self.pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=180) # type: ignore
        self.servo1 = servo.Servo(self.pca.channels[1], min_pulse=500, max_pulse=2200, actuation_range=153) # type: ignore

# Reset the motor to a start position with a pause
# otherwise there is sometimes an IO error.
        self.servo0.angle = 90
        self.servo1.angle = 90
        time.sleep(1)
# -----------------------------------

# -----------------------------------
    def deinit(self):
        self.pca.channels[0].duty_cycle = 0
        self.pca.channels[1].duty_cycle = 0
        self.pca.deinit()
        self.i2c.unlock()
        self.i2c.deinit()
# -----------------------------------

# -----------------------------------
    def _calibrate(self):
        input("Press enter when ready to measure default frequency.")
        # Set the PWM duty cycle for channel zero to 50%. 
        # duty_cycle is 16 bits to match other PWM objects
        # but the PCA9685 will only actually give 12 bits of resolution.
        print("Running with default calibration")
        self.pca.channels[0].duty_cycle = 0x7FFF
        time.sleep(5)
        self.pca.channels[0].duty_cycle = 0

        measured_frequency = float(input("Frequency measured: "))
        print()

        self.pca.reference_clock_speed = int(self.pca.reference_clock_speed * (measured_frequency / self.pca.frequency))
        # Set frequency again so we can get closer. 
        # Reading it back will produce the real value.
        input("Press enter when ready to measure coarse calibration frequency.")
        self.pca.channels[0].duty_cycle = 0x7FFF
        time.sleep(5)
        self.pca.channels[0].duty_cycle = 0
        measured_after_calibration = float(input("Frequency measured: "))
        print()

        reference_clock_speed = measured_after_calibration * 4096 * self.pca.prescale_reg
        print(f"Real reference clock speed: {reference_clock_speed:.0f}")
# -----------------------------------


if __name__ == "__main__":

    servos = Servos()
    # We sleep in the loops to give the servo time to move into position.
    print("forward")
    servos.servo0.angle = 0
    time.sleep(0.5)
    for i in range(180):
        servos.servo0.angle = i
        time.sleep(0.01)
    print("backward")
    for i in range(180):
        servos.servo0.angle = 180 - i
        time.sleep(0.01)
    servos.servo0.angle=90
    time.sleep(1.0)


    servos.servo1.angle = 0
    time.sleep(0.5)
    for i in range(153):
        servos.servo1.angle = i
        time.sleep(0.01)
    print("backward")
    for i in range(153):
        servos.servo1.angle = 153 - i
        time.sleep(0.01)
    servos.servo1.angle=90
    time.sleep(0.5)
    servos.deinit()


