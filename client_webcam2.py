# Import necessary modules
import sys
import socket
import threading
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QWidget, QLabel
from PyQt5.QtCore import Qt
import cv2

# Define the Client class which inherits from QMainWindow
from PyQt5.QtWidgets import QComboBox

class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.isConnected = False
        self.capture = None
        self.video_writer = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Client')
        self.setGeometry(100, 100, 400, 400)
        layout = QVBoxLayout()

        self.ipInput = QLineEdit(self)
        self.ipInput.setPlaceholderText('Server IP')
        self.ipInput.setText('10.91.77.8')
        layout.addWidget(self.ipInput)

        self.portInput = QLineEdit(self)
        self.portInput.setPlaceholderText('Port')
        self.portInput.setText('9999')
        layout.addWidget(self.portInput)

        # 添加摄像头端口选择
        self.cameraPortInput = QComboBox(self)
        self.cameraPortInput.addItems(['0', '1', '2', '3', '4'])  # 假设最多有5个摄像头
        layout.addWidget(self.cameraPortInput)

        self.connectBtn = QPushButton('Connect', self)
        self.connectBtn.clicked.connect(self.start_connection)
        layout.addWidget(self.connectBtn)

        self.statusLabel = QLabel('Status: Disconnected', self)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.statusLabel)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_connection(self):
        ip = self.ipInput.text()
        port = int(self.portInput.text())
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.isConnected = True
            self.statusLabel.setText('Status: Connected')
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            print(f"Connection failed: {e}")
        # try:
        #     self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.client_socket.connect((ip, port))
        #     self.isConnected = True
        #     self.statusLabel.setText('Status: Connected')

        #     self.capture = cv2.VideoCapture(camera_port)
        #     if not self.capture.isOpened():
        #         raise Exception("Cannot open webcam")
        #     self.video_writer = cv2.VideoWriter(
        #         os.path.join(self.save_directory, 'rgb_video.avi'),
        #         cv2.VideoWriter_fourcc(*'XVID'), 30, (3480, 2160))
        # except Exception as e:
        #     self.statusLabel.setText(f'Error: {e}')
        #     self.isConnected = False

    def receive_message(self):
        while self.isConnected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == "start_click":
                    self.start_video_capture()
                elif message == "stop_click":
                    self.stop_video_capture()
                else:
                    directory = message
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    self.save_directory = directory
                    # Start capturing video from the first webcam
                    camera_port = int(self.cameraPortInput.currentText())  # 从下拉菜单获取摄像头端口
                    self.capture = cv2.VideoCapture(camera_port)
                    if not self.capture.isOpened():
                        raise Exception("Cannot open webcam")
                    # Initialize video writer for saving the RGB video
                    self.video_writer = cv2.VideoWriter(os.path.join(self.save_directory, 'rgb_video.avi'), cv2.VideoWriter_fourcc(*'XVID'), 30, (3480, 2160))
            except Exception as e:
                self.statusLabel.setText(f'Error: {e}')
                self.isConnected = False
                break

    def start_video_capture(self):
        # Start capturing video from the first webcam
        # self.capture = cv2.VideoCapture(0)
        # if not self.capture.isOpened():
            # raise Exception("Cannot open webcam")
        # Initialize video writer for saving the RGB video
        # self.video_writer = cv2.VideoWriter(os.path.join(self.save_directory, 'rgb_video.avi'), cv2.VideoWriter_fourcc(*'XVID'), 30, (3480, 2160))
        threading.Thread(target=self.capture_video, daemon=True).start()

    def capture_video(self):
        try:
            while self.capture.isOpened():
                ret, frame = self.capture.read()
                if not ret:
                    break
                self.video_writer.write(frame)
        except Exception as e:
            print(f"Error capturing video: {e}")

    def stop_video_capture(self):
        if self.capture:
            self.capture.release()
            self.video_writer.release()
            self.capture = None
            self.video_writer = None
            print("Video capture stopped and saved.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec_())