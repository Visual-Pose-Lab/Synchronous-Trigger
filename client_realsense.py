import sys
import socket
import threading
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QWidget, QLabel, QInputDialog
from PyQt5.QtCore import Qt, QTimer
import pyrealsense2 as rs
import numpy as np
import cv2

class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.isConnected = False
        self.pipeline = None
        self.depth_video = None
        self.rgb_video = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Client')
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()
        
        self.ipInput = QLineEdit(self)
        self.ipInput.setPlaceholderText('Server IP')
        self.ipInput.setText('192.168.1.1')  # 设置默认IP地址
        layout.addWidget(self.ipInput)
        
        self.portInput = QLineEdit(self)
        self.portInput.setPlaceholderText('Port')
        self.portInput.setText('9999')  # 设置默认端口号
        layout.addWidget(self.portInput)
        
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
            self.statusLabel.setText(f'Connection Failed: {e}')

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
            except Exception as e:
                self.statusLabel.setText(f'Error: {e}')
                self.isConnected = False
                break

    def start_video_capture(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        # config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 90)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(config)
        self.depth_video = cv2.VideoWriter(os.path.join(self.save_directory, 'depth_video.avi'), 
                                           cv2.VideoWriter_fourcc(*'XVID'), 90, (640, 480), False)
        self.rgb_video = cv2.VideoWriter(os.path.join(self.save_directory, 'rgb_video.avi'), 
                                         cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
        threading.Thread(target=self.capture_video, daemon=True).start()

    def capture_video(self):
        try:
            cnt = 0
            while self.pipeline:
                frames = self.pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if not depth_frame or not color_frame:
                    continue
                
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                depth_image_8bit = cv2.convertScaleAbs(depth_image, alpha=0.03)
                self.depth_video.write(depth_image_8bit)
                if cnt % 3 == 0:  
                    self.rgb_video.write(color_image)
                cnt += 1
        except Exception as e:
            print(f"Error capturing video: {e}")

    def stop_video_capture(self):
        if self.pipeline:
            self.pipeline.stop()
            self.pipeline = None
            self.depth_video.release()
            self.rgb_video.release()
            self.depth_video = None
            self.rgb_video = None
            print("Video capture stopped and saved.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec_())
