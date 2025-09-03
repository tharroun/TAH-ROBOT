import sys
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/pyside')


from PySide6.QtWidgets import (
    QApplication, 
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
)
from PySide6.QtCore import (
    Qt,
)
from PySide6.QtGui import (
    QCloseEvent,
)
import PySide6.QtAsyncio as QtAsyncio

import asyncio



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self._makeUI()
        
        self.running_gamepad = False

    def _makeUI(self):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setGeometry(0,0,200, 480)
    
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.quit_clicked = False
        self.buttonQuit = QPushButton("Quit Program", self)
        self.buttonQuit.clicked.connect(self.quit_program)

        self.buttonGamepad = QPushButton("Start Gamepad", self)
        self.buttonGamepad.clicked.connect(lambda: asyncio.ensure_future(self.run_gamepad()))
        
        self.buttonTest = QPushButton("Test", self)
        self.buttonTest.clicked.connect(self.test_click)

        main_layout.addWidget(self.buttonQuit) 
        main_layout.addWidget(self.buttonGamepad) 
        main_layout.addWidget(self.buttonTest)
        main_layout.addStretch(1)

    async def run_gamepad(self):
        #Do not lanuch more than one gamepad async process
        if self.running_gamepad : return

        self.buttonGamepad.setText("Running")
        self.running_gamepad = True
        for i in range(20):
            await asyncio.sleep(0.5)
            print(i)
        self.buttonGamepad.setText("Start Gamepad")
        self.running_gamepad = False
        return

    def test_click(self):
        print(self.running_gamepad)
        return

    def quit_program(self):
        self.quit_clicked = True
        self.close()

    def closeEvent(self, event: QCloseEvent):
        if self.quit_clicked:
            print("Closing")
            event.accept() # let the window close
        else:
            event.ignore()
        return

def main():
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    #sys.exit(app.exec())
    QtAsyncio.run(handle_sigint=True)

if __name__ == "__main__":
    main()