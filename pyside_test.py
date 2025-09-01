import sys
from PySide6.QtWidgets import (
    QApplication, 
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QCloseEvent,
)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self._makeUI()
        

    def _makeUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.quit_clicked = False
        self.button = QPushButton("Quit Program", self)
        self.button.clicked.connect(self.quit_program)
        
        main_layout.addWidget(self.button) 
        main_layout.addStretch()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.resize(200, 480)
        self.move(0, 0)


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
    sys.exit(app.exec())

if __name__ == "__main__":
    main()