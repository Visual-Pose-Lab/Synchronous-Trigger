import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import pyqtSlot
import socket
import threading

class Server(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.server = None
        self.clients = []
        self.is_running = False

    def initUI(self):
        self.setWindowTitle('Server Control Panel')
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        
        self.infoLabel = QLabel('Server is not running')
        self.layout.addWidget(self.infoLabel)
        
        self.clientsLabel = QLabel('Connected Clients:')
        self.layout.addWidget(self.clientsLabel)
        
        self.startBtn = QPushButton('Start Server', self)
        self.startBtn.clicked.connect(self.start_server)
        self.layout.addWidget(self.startBtn)
        
        self.stopBtn = QPushButton('Stop Server', self)
        self.stopBtn.clicked.connect(self.stop_server)
        self.layout.addWidget(self.stopBtn)
        
        self.sendBtn = QPushButton('Send Click Command', self)
        self.sendBtn.clicked.connect(self.send_click_command)
        self.layout.addWidget(self.sendBtn)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    @pyqtSlot()
    def start_server(self):
        if not self.is_running:
            self.is_running = True
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 添加这行代码
            self.server.bind(('0.0.0.0', 9999))
            self.server.listen(5)
            threading.Thread(target=self.accept_connections, daemon=True).start()
            self.infoLabel.setText('Server is running on port 9999')

    # def start_server(self):
    #     if not self.is_running:
    #         self.is_running = True
    #         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         self.server.bind(('0.0.0.0', 9999))
    #         self.server.listen(5)
    #         threading.Thread(target=self.accept_connections, daemon=True).start()
    #         self.infoLabel.setText('Server is running on port 9999')

    @pyqtSlot()
    def stop_server(self):
        if self.is_running:
            self.is_running = False
            for client in self.clients:
                client.close()
            self.server.close()
            self.clients.clear()
            self.clientsLabel.setText('Connected Clients:')
            self.infoLabel.setText('Server is not running')

    @pyqtSlot()
    def send_click_command(self):
        if self.is_running:
            for client in self.clients:
                client.sendall(b'click')
            self.infoLabel.setText('Click command sent to all clients')

    def accept_connections(self):
        while self.is_running:
            client, addr = self.server.accept()
            self.clients.append(client)
            self.update_clients_label()
            print(f"Connection established with {addr}")

    def update_clients_label(self):
        clients_info = 'Connected Clients:\n' + '\n'.join([f"{idx+1}. {c.getpeername()[0]}" for idx, c in enumerate(self.clients)])
        self.clientsLabel.setText(clients_info)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Server()
    ex.show()
    sys.exit(app.exec_())
