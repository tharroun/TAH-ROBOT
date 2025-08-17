#!/usr/bin/env python3
# coding=utf8
import sys
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')

from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QGridLayout, 
    QPushButton, 
    QDial, 
    QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent

import ybmc

class RobotControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ybmc = ybmc.YBMC()
        
        self.setWindowTitle("Robot Control")
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        #--------------------------------------
        # Create horizontal layout for go/stop buttons
        button_layout = QHBoxLayout()
        
        # Create Go button
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.robot_go)
        self.go_button.setMinimumHeight(40)
        self.go_style = self.go_button.styleSheet()
        
        # Create Stop button
        self.stop_button = QPushButton("Stop all")
        self.stop_button.clicked.connect(self.robot_stop)
        self.stop_button.setMinimumHeight(40)

        # Create Stop spin button
        self.spin_button = QPushButton("Stop spin")
        self.spin_button.clicked.connect(self.robot_stop_spin)
        self.spin_button.setMinimumHeight(40)
        
        # Add buttons to horizontal layout
        button_layout.addWidget(self.go_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.spin_button)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        #-------------------------------------

        #--------------------------------------
        # Create grid layout for speed and direction control
        speed_layout = QGridLayout()
        
        # Create direction dial control
        self.direction_title = QLabel("Direction")
        self.direction_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.direction_dial = QDial()
        self.direction_dial.setRange(-180, 180)
        self.direction_dial.setWrapping(True)
        self.direction_dial.setSingleStep(20)
        self.direction_dial.setNotchesVisible(True)
        self.direction_dial.setTracking(False)
        self.direction_dial.setMinimumHeight(80)
        self.direction_dial.valueChanged.connect(self.direction_value_changed)
        self.direction_value = QLabel("0")
        self.direction_value.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # Create speed dial control
        self.speed_title = QLabel("Speed")
        self.speed_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.speed_dial = QDial()
        self.speed_dial.setRange(0,1500)
        self.speed_dial.setWrapping(False)
        self.speed_dial.setSingleStep(20)
        self.speed_dial.setNotchesVisible(True)
        self.speed_dial.setTracking(False)
        self.speed_dial.setMinimumHeight(80)
        self.speed_dial.valueChanged.connect(self.speed_value_changed)
        self.speed_value = QLabel("0")
        self.speed_value.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # Create spin dial control
        self.spin_title = QLabel("Spin")
        self.spin_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.spin_dial = QDial()
        self.spin_dial.setRange(-1000, 1000)
        self.spin_dial.setWrapping(False)
        self.spin_dial.setSingleStep(20)
        self.spin_dial.setNotchesVisible(True)
        self.spin_dial.setTracking(False)
        self.spin_dial.setMinimumHeight(80)
        self.spin_dial.valueChanged.connect(self.spin_value_changed)
        self.spin_value = QLabel("0")
        self.spin_value.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # Add dials to grid layout
        speed_layout.addWidget(self.direction_title,0,0)
        speed_layout.addWidget(self.speed_title,    0,1)
        speed_layout.addWidget(self.spin_title,     0,2)
        speed_layout.addWidget(self.direction_dial, 1,0)
        speed_layout.addWidget(self.speed_dial,     1,1)
        speed_layout.addWidget(self.spin_dial,      1,2)
        speed_layout.addWidget(self.direction_value,2,0)
        speed_layout.addWidget(self.speed_value,    2,1)
        speed_layout.addWidget(self.spin_value,     2,2)
        # Add grid layout to main layout
        main_layout.addLayout(speed_layout)
        #-------------------------------------

        #-------------------------------------
        # Creat battery row
        battery_layout = QHBoxLayout()
        self.battery_motor_title = QLabel("Motor battery")
        self.battery_motor_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.battery_motor_value = QLabel("0.0V")
        self.battery_motor_value.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.battery_motor_value_style = self.battery_motor_value.styleSheet()
        battery_layout.addWidget(self.battery_motor_title)
        battery_layout.addWidget(self.battery_motor_value)
        main_layout.addLayout(battery_layout)
        #-------------------------------------

        # Add stretch to push buttons to top
        main_layout.addStretch()

        self.get_batteries()
        self.is_running = False
    
            
    def closeEvent(self, event: QCloseEvent):
        print("Closing")
        self.robot_stop()
        self.ybmc.stopYBMC()
        event.accept() # let the window close
        return

    def get_batteries(self):
        # MOTOR BATTRY
        str = self.ybmc.get_battery()
        try:
            val = float(str[:-1])
            if val < 9.8 :
                self.battery_motor_value.setStyleSheet('QLabel {background-color: #EA1A1A; color: black;}')
            elif val >= 9.8 and val < 11.8 :
                self.battery_motor_value.setStyleSheet('QLabel {background-color: #EAF523; color: black;}')
            else :
                self.battery_motor_value.setStyleSheet('QLabel {background-color: #21ED1A; color: black;}')

        except:
            self.battery_motor_value.setStyleSheet(self.battery_motor_value_style)
            pass
        self.battery_motor_value.setText(str)
        return

    def robot_go(self):
        """Function called when Go button is pressed"""
        self.ybmc.set_velocity(float(self.speed_dial.value()), 
                               float(self.direction_dial.value()), 
                               float(self.spin_dial.value()))
        self.is_running = True
        self.go_button.setStyleSheet('QPushButton {background-color: #21ED1A; color: black;}')
        self.go_button.setText("Running")
        self.get_batteries()
        
    def robot_stop(self):
        """Function called when Stop button is pressed"""
        self.ybmc.control_pwm(0,0,0,0)
        self.is_running = False
        #self.speed_dial.setValue(0)
        self.go_button.setStyleSheet(self.go_style)
        self.go_button.setText("Go")
        self.get_batteries()
    
    def direction_value_changed(self, i):
        if self.is_running:
            self.ybmc.set_velocity(float(self.speed_dial.value()), 
                                   float(i), 
                                   float(self.spin_dial.value()))
        self.direction_value.setText(f"{i}")
        self.get_batteries()

    def speed_value_changed(self, i):
        if self.is_running:
            self.ybmc.set_velocity(float(i), 
                                   float(self.direction_dial.value()), 
                                   float(self.spin_dial.value()))
        self.speed_value.setText(f"{i}")
        self.get_batteries()
    
    def spin_value_changed(self, i):
        if self.is_running:
            self.ybmc.set_velocity(float(self.speed_dial.value()), 
                                   float(self.direction_dial.value()), 
                                   float(i))
        self.spin_value.setText(f"{i}")
        self.get_batteries()
    
    def robot_stop_spin(self, i):
        if self.is_running:
            self.ybmc.set_velocity(float(self.speed_dial.value()), 
                                   float(self.direction_dial.value()), 
                                   0)
        self.spin_dial.setValue(0)
        self.spin_value.setText(f"{0}")
        self.get_batteries()

def main():
    app = QApplication(sys.argv)
    window = RobotControlApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
