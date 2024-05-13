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
# Define the Client class which inherits from QMainWindow
class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.isConnected = False
        self.isCapturing = False
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
        self.cameraPortInput.addItems(['0', '1', '2', '3', '4', '5'])  # 假设最多有5个摄像头
        layout.addWidget(self.cameraPortInput)

        # 添加分辨率选择
        self.cameraResolutionInput = QComboBox(self)
        self.cameraResolutionInput.addItems(['640x480', '800x600', '960x720', '1280x720', '1280x960', '1920x1080', '2560x1440', '3840x2160'])
        layout.addWidget(self.cameraResolutionInput)
        print(self.cameraResolutionInput.currentText())
        print(type(self.cameraResolutionInput.currentText()))

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
                    # width, height = 1280, 720
                    print(camera_port)
                    width = int(self.cameraResolutionInput.currentText().split("x")[0]) # 获取分辨率
                    height = int(self.cameraResolutionInput.currentText().split("x")[1])  # 获取分辨率
                    print(width, height)
                    # self.capture = cv2.VideoCapture(1)
                    self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                    
                    if not self.capture.isOpened():
                        raise Exception("Cannot open webcam")
                    # Initialize video writer for saving the RGB video
                    self.video_writer = cv2.VideoWriter(os.path.join(self.save_directory, 'rgb_video.avi'), cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))

            except Exception as e:
                self.statusLabel.setText(f'Error: {e}')
                self.isConnected = False
                break

    def start_video_capture(self):
        
        # Start capturing video from the first webcam
        # self.capture = cv2.VideoCapture(0)
        # if not self.capture.isOpened():
        #     raise Exception("Cannot open webcam")
        # Initialize video writer for saving the RGB video
        # self.video_writer = cv2.VideoWriter(os.path.join(self.save_directory, 'rgb_video.avi'), cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
        threading.Thread(target=self.capture_video, daemon=True).start()

    def capture_video(self):
        self.isCapturing = True
        try:
            while self.capture.isOpened() and self.isCapturing:
                ret, frame = self.capture.read()
                if not ret:
                    break
                self.video_writer.write(frame)
        except Exception as e:
            print(f"Error capturing video: {e}")
        finally:
            print("Capture loop has exited.")

    def stop_video_capture(self):
        self.isCapturing = False  # 停止捕获循环
        # 确保循环已经完全停止
        while self.capture.isOpened() and not self.isCapturing:
            continue  # 等待捕获线程完全停止
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