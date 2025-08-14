#!/usr/bin/env python3
# coding=utf8
import sys
sys.path.append('/home/tah/Github/TAH-ROBOT')
sys.path.append('/home/tah/Github/TAH-ROBOT/motors')

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QDial, QLabel
from PyQt6.QtCore import Qt

import ybmc

class RobotControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ybmc = ybmc.YBMC()
        self.ybmc.get_battery()

        
        self.setWindowTitle("Robot Control")
        self.setGeometry(100, 100, 400, 250)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        #--------------------------------------
        # Create horizontal layout for buttons
        button_layout = QHBoxLayout()
        
        # Create Go button
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.robot_go)
        self.go_button.setMinimumHeight(40)
        
        # Create Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.robot_stop)
        self.stop_button.setMinimumHeight(40)
        
        # Add buttons to horizontal layout
        button_layout.addWidget(self.go_button)
        button_layout.addWidget(self.stop_button)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        #-------------------------------------

        #--------------------------------------
        # Create grid layout for buttons
        speed_layout = QGridLayout()
        
        # Create Direction dial
        self.direction_title = QLabel("Direction")
        self.direction_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.direction_dial = QDial()
        self.direction_dial.setRange(-180, 180)
        self.direction_dial.setWrapping(True)
        self.direction_dial.setSingleStep(20)
        self.direction_dial.setNotchesVisible(True)
        self.direction_dial.setTracking(False)
        self.direction_dial.valueChanged.connect(self.direction_value_changed)
        self.direction_value = QLabel("0")
        self.direction_value.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)


        # Create Speed slider
        self.speed_title = QLabel("Speed")
        self.speed_title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.speed_dial = QDial()
        self.speed_dial.setRange(0,1500)
        self.speed_dial.setWrapping(False)
        self.speed_dial.setSingleStep(20)
        self.speed_dial.setNotchesVisible(True)
        self.speed_dial.setTracking(False)
        self.speed_dial.valueChanged.connect(self.speed_value_changed)
        self.speed_value = QLabel("0")
        self.speed_value.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # Add buttons to horizontal layout
        speed_layout.addWidget(self.direction_title,0,0)
        speed_layout.addWidget(self.speed_title,0,1)
        speed_layout.addWidget(self.direction_dial,1,0)
        speed_layout.addWidget(self.speed_dial,1,1)
        speed_layout.addWidget(self.direction_value,2,0)
        speed_layout.addWidget(self.speed_value,2,1)
        
        # Add button layout to main layout
        main_layout.addLayout(speed_layout)
         #-------------------------------------

        # Add stretch to push buttons to top
        main_layout.addStretch()
    
            
    def closeEvent(self, event):
        # do stuff
        print("Closing")
        self.robot_stop()
        self.ybmc.stopYBMC()
        event.accept() # let the window close

    def robot_go(self):
        """Function called when Go button is pressed"""
        self.ybmc.set_velocity(float(self.speed_dial.value()), 
                               float(self.direction_dial.value()), 
                               0.0)
        
    def robot_stop(self):
        """Function called when Stop button is pressed"""
        self.ybmc.control_pwm(0,0,0,0)
        #self.speed_dial.setValue(0)
    
    def direction_value_changed(self, i):
        self.ybmc.set_velocity(float(self.speed_dial.value()), 
                               float(i), 
                               0.0)
        self.direction_value.setText(f"{i}")

    def speed_value_changed(self, i):
        self.ybmc.set_velocity(float(i), 
                               float(self.direction_dial.value()), 
                               0.0)
        self.speed_value.setText(f"{i}")

def main():
    app = QApplication(sys.argv)
    window = RobotControlApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
