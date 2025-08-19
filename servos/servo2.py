import time
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

i2c = board.I2C()  # uses board.SCL and board.SDA

# Create a simple PCA9685 class instance.
#pca = PCA9685(i2c, reference_clock_speed=25600000)
pca = PCA9685(i2c)
pca.frequency = 50
# To get the full range of the servo you will likely need to adjust the min_pulse and max_pulse to
# match the stall points of the servo.
servo0 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=180)
servo2 = servo.Servo(pca.channels[2], min_pulse=500, max_pulse=2500, actuation_range=180)

# Reset the motor to a start position with a pause
# otherwise there is sometimes an IO error.
servo0.angle = 0
servo2.angle = 0
time.sleep(1)

# We sleep in the loops to give the servo time to move into position.
print("forward")
for i in range(180):
    servo0.angle = i
    servo2.angle = i
    time.sleep(0.005)
print("backward")
for i in range(180):
    servo0.angle = 180 - i
    servo2.angle = 180 - i
    time.sleep(0.005)

# You can also specify the movement fractionally.
print("forward fractionally")
fraction = 0.0
while fraction < 1.0:
    servo0.fraction = fraction
    servo2.fraction = fraction
    fraction += 0.01
    time.sleep(0.03)

pca.channels[0].duty_cycle = 0
pca.channels[2].duty_cycle = 0
i2c.unlock()
i2c.deinit()
