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
- Add the super-structure and cover
- Add mmounting bracket for the touch screen
- Attach the pan-tilt servo to the super-structure
- What is the deadtime for the 520 motor?

### Programming
- Control program
    - Remove the logger and add a text window to show messages 
    - Add a button and label to monitor wheel speeds
    - Include a PID control adjustment tool
- Motor control
    - Test using the YB speed control
    - Failing that, make my own speed control tuner using PWM
- Pan-tilt
    - Write pan tilt control SDK

