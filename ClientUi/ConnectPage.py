from PyQt5 import QtWidgets, QtCore

class ConnectPage(QtWidgets.QDialog):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        

        self.connect_button = QtWidgets.QPushButton("Connect")

        self.status = QtWidgets.QLabel("Status: disconnected")

        self.button_layout = QtWidgets.QHBoxLayout()

        self.button_layout.addWidget(self.connect_button, stretch=1)
        self.button_layout.addWidget(self.status, stretch=5)

        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.addLayout(self.button_layout)

        self.backend.update_connection_status_signal.connect(self.backend_connection_status_update_slot)
        self.connect_button.pressed.connect(self.connection_button_pressed_slot)

    def connection_button_pressed_slot(self):
        if self.connect_button.text() == 'Connect':
            self.backend.connection_req.emit(self.backend.ConnectionRequest.CONNECT)
        if self.connect_button.text() == 'Cancel':
            self.backend.connection_req.emit(self.backend.ConnectionRequest.CANCEL)
        if self.connect_button.text() == 'Disconnect':
            self.backend.connection_req.emit(self.backend.ConnectionRequest.DISCONNECT)
        pass

    def backend_connection_status_update_slot(self, status):
        if status == self.backend.ConnectionStatus.DISCONNECTED:
            self.status.setText("Status: disconnected")
            self.connect_button.setText("Connect")
        elif status == self.backend.ConnectionStatus.CONNECTING:
            self.status.setText("Status: connecting")
            self.connect_button.setText("Cancel")
        elif status == self.backend.ConnectionStatus.CONNECTED:
            self.status.setText("Status: connected")
            self.connect_button.setText("Disconnect")
        pass

