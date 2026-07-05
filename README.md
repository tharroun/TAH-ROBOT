# TAH-ROBOT


<img width="2362" height="892" alt="TAH-ROBOT drawio" src="https://github.com/user-attachments/assets/4034f403-4f1b-4354-bff3-2f42e2649780" />

## Servo control
We are using the Adafruit library for the MZ996R servos on the PCA9685 16-channel board

## Seeting up github
```
sudo apt install git
sudo apt install gh
git config --global user.name tharroun
get config --global user.email thad.harroun@gmail.com
gh aith login
>> GitHub.com
>> SSH
>> 
```

## Needed files in venv
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

### Programming
- Add `join`s for the two main JoinableQueues.

### Construction

### Next steps
- Motors
    - what is the deadtime for the 520 motor?
    - calibrate the speed using the encoders
- Servos
    - how to find the max/min without collision of the servo?
    - how to more easily re-center the servos?
- Wishlist
    - LIDAR?
    - NVMe SSD on RPi

