import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QColor
import socket
import threading
from pynput.mouse import Listener
import pyautogui

class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.client_socket = None
        self.isConnected = False
        self.mouse_click_position = (122, 231)  # Initialize with a default position

    def initUI(self):
        self.setWindowTitle('OpenCap Client')
        self.setGeometry(100, 100, 400, 220)
        
        layout = QVBoxLayout()
        
        self.ipInput = QLineEdit(self)
        self.ipInput.setPlaceholderText('Server IP')
        self.ipInput.setText('192.168.31.176')  # 设置默认IP地址
        layout.addWidget(self.ipInput)
        
        self.portInput = QLineEdit(self)
        self.portInput.setPlaceholderText('Port')
        self.portInput.setText('9999')  # 设置默认端口号
        layout.addWidget(self.portInput)
        
        self.startBtn = QPushButton('Start', self)
        self.startBtn.clicked.connect(self.start_connection)
        layout.addWidget(self.startBtn)
        

        self.setPositionBtn = QPushButton('Set Click Position', self)
        self.setPositionBtn.clicked.connect(self.set_click_position)
        layout.addWidget(self.setPositionBtn)

        self.statusLabel = QLabel('Status: Disconnected', self)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.statusLabel)

        self.connectionStatus = QLabel(self)
        self.connectionStatus.setStyleSheet("background-color: red")
        self.connectionStatus.setFixedHeight(20)
        layout.addWidget(self.connectionStatus)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.blink_status)
        self.blink = False

    @pyqtSlot()
    def start_connection(self):
        ip = self.ipInput.text()
        port = int(self.portInput.text())
        self.connect_to_server(ip, port)

    @pyqtSlot()
    def set_click_position(self):
        # Use pynput to listen for a single click to record the position
        listener = Listener(on_click=self.on_click)
        listener.start()
        listener.join()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.mouse_click_position = (x, y)
            print(f"Click position set to: {self.mouse_click_position}")
            return False  # Stop listener after the first click

    def connect_to_server(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((ip, port))
            self.isConnected = True
            self.statusLabel.setText('Status: Connected')
            self.connectionStatus.setStyleSheet("background-color: green")
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            print(e)
            self.isConnected = False
            self.statusLabel.setText('Status: Disconnected')
            self.connectionStatus.setStyleSheet("background-color: red")
            self.timer.start(500)

    def receive_message(self):
        while self.isConnected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == "start_click" or message == "stop_click":
                    print("Received message:", message)
                    # Simulate click at the recorded position when a specific message is received
                    pyautogui.click(self.mouse_click_position[0], self.mouse_click_position[1])
                elif message != "start_click" and message !=  "stop_click":
                    print("Received message:", message, ", Do nothing")
                else:
                    self.isConnected = False
                    self.timer.start(500)
            except:
                self.isConnected = False
                self.timer.start(500)
                break

    def blink_status(self):
        if self.blink:
            self.connectionStatus.setStyleSheet("background-color: red")
            self.blink = False
        else:
            self.connectionStatus.setStyleSheet("background-color: none")
            self.blink = True
        if self.isConnected:
            self.timer.stop()
            self.connectionStatus.setStyleSheet("background-color: green")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Client()
    ex.show()
    sys.exit(app.exec_())
