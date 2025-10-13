# TAH-ROBOT


<img width="2591" height="731" alt="flow drawio" src="https://github.com/user-attachments/assets/c806c86f-ade7-41e9-84ff-45a436a2bca9" />

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
    - add pid control to the motors
    - tune pid for the servos
- Motors
    - what is the deadtime for the 520 motor?
    - calibrate the speed using the encoders
- Servos
    - how to find the max/min of the servo?
    - how to re-center the servos?

