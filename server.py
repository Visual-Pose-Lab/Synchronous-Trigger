import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QTextEdit
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

        self.messageInput = QLineEdit(self)
        self.messageInput.setText('sub01_W1')
        self.layout.addWidget(self.messageInput)
        
        self.sendCustomMsgBtn = QPushButton('Send Message', self)
        self.sendCustomMsgBtn.clicked.connect(self.send_custom_message)
        self.layout.addWidget(self.sendCustomMsgBtn)
        
        self.sendBtn = QPushButton('Send Start Command', self)
        self.sendBtn.clicked.connect(self.send_start_click)
        self.layout.addWidget(self.sendBtn)
        
        self.sendDoubleClickBtn = QPushButton('Send Stop Command', self)
        self.sendDoubleClickBtn.clicked.connect(self.send_stop_click)
        self.layout.addWidget(self.sendDoubleClickBtn)
        
        # GUI Enhancement: Add a log text area for server actions and messages
        self.logTextArea = QTextEdit(self)
        self.logTextArea.setReadOnly(True)
        self.layout.addWidget(self.logTextArea)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    @pyqtSlot()
    def start_server(self):
        if not self.is_running:
            self.is_running = True
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', 9999))
            self.server.listen(5)
            threading.Thread(target=self.accept_connections, daemon=True).start()
            self.infoLabel.setText('Server is running on port 9999')
            self.log_message("Server started on port 9999")

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
            self.log_message("Server stopped.")

    @pyqtSlot()
    def send_start_click(self):
        if self.is_running:
            for client in self.clients:
                client.sendall(b'start_click')
            self.infoLabel.setText('Start click command sent to all clients')
            self.log_message('Start click command sent to all clients')

    @pyqtSlot()
    def send_stop_click(self):
        if self.is_running:
            for client in self.clients:
                client.sendall(b'stop_click')
            self.infoLabel.setText('Stop click command sent to all clients')
            self.log_message('Stop click command sent to all clients')

    @pyqtSlot()
    def send_custom_message(self):
        if self.is_running:
            custom_msg = self.messageInput.text().encode('utf-8')
            for client in self.clients:
                client.sendall(custom_msg)
            self.infoLabel.setText('Custom message sent to all clients')
            self.log_message(f'Custom message "{self.messageInput.text()}" sent to all clients')

    def accept_connections(self):
        while self.is_running:
            client, addr = self.server.accept()
            self.clients.append(client)
            self.update_clients_label()
            self.log_message(f"Connection established with {addr}")
      

    def update_clients_label(self):
        clients_info = 'Connected Clients:\n' + '\n'.join([f"{idx+1}. {c.getpeername()[0]}" for idx, c in enumerate(self.clients)])
        self.clientsLabel.setText(clients_info)

    def log_message(self, message):
        """Method to append messages to the log text area."""
        self.logTextArea.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Server()
    ex.show()
    sys.exit(app.exec_())
