# TAH-ROBOT

## Servo control
We are using the Adafruit library for the MZ996R servos on the PCA9685 16-channel board
```
sudo apt install joystick
apt install python3-pyqt6
apt install python3-opencv
apt install rpicamera
cd TAH-ROBOT
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip3 install adafruit-circuitpython-pca9685
pip3 install lgpio
pip3 install adafruit-circuitpython-motor
pip3 install evdev
```

## To-do list

### Construction

### Programming
- Drive
    - Need to add text messages to the 
    - Add a button and label to monitor wheel speeds
    - Include a PID control adjustment tool
- Motors
    - What is the deadtime for the 520 motor?
    - Test using the YB speed control
    - Failing that, make my own speed control tuner using PWM
- Servos
    - How to find the max/min of the servo?
    - How to re-center the servos?

