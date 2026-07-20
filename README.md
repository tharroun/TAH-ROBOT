# TAH-ROBOT


<img width="2362" height="892" alt="TAH-ROBOT drawio" src="https://github.com/user-attachments/assets/4034f403-4f1b-4354-bff3-2f42e2649780" />

## Servo control
Adafruit library for the MZ996R servos on the PCA9685 16-channel board

## Motors and control
Yahboom 520 motors and the Yahboom 4-motor controller.

## Power
Yahboom 5V power control
Two, 12V battery packs (One for the motor controler, one for the 5V Pi/Camera/display/servos)

## Seeting up github
```
sudo apt install git
sudo apt install gh
git config --global user.name tharroun
git config --global user.email thad.harroun@xxxxx.xxx
gh auth login
>> GitHub.com
>>> etc.
gh repo clone tharroun/TAH-ROBOT
```

## Needed files in venv
```
sudo apt install joystick
apt install python3-pyqt6
apt install python3-opencv
apt install rpicam-apps
cd TAH-ROBOT
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip3 install adafruit-circuitpython-pca9685
pip3 install lgpio
pip3 install adafruit-circuitpython-motor
pip3 install evdev
```

## To-do list

### Programming
- Save motor encoder calibration to a yaml file

### Construction
- Raise the camera
- Build a protective top
- Switch screens to the 5-inch LCD?

### Next steps
- Motors
    - what is the deadtime for the 520 motor?
- Servos
    - how to find the max/min without collision of the servo?
    - how to more easily re-center the servos?
- Wishlist
    - LIDAR?
    - NVMe SSD on RPi

