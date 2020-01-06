from enum import Enum
from PyQt5 import QtWidgets, QtCore

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DictionaryDataStreamer import DictionaryDataStreamer

class AppBackend():
    def __init__(self):
        self.streamer = DictionaryDataStreamer(name='long_2', domain='hoanglong-desktop',\
            password='123')
        self.streamer.connect(block=True)
        self.workstation_list = []

    def createWorkstationBackend(self, workstation_address):
        return WorkstationBackend(workstation_address)

    def getWorkstationList(self):
        return self.streamer.getListOfPeers()

class WorkstationBackend(QtCore.QObject):
    class ConnectionStatus(Enum):
        DISCONNECTED = 0
        CONNECTING = 1
        CONNECTED = 2
    
    class ConnectionRequest(Enum):
        CONNECT = 0
        CANCEL = 1
        DISCONNECT = 2

    connection_req = QtCore.pyqtSignal(ConnectionRequest)
    update_connection_status_signal = QtCore.pyqtSignal(ConnectionStatus)

    def __init__(self, workstation_address, parent=None):
        super().__init__(parent)
        self.address = workstation_address
        self.connection_status = self.ConnectionStatus.DISCONNECTED
        self.connection_req.connect(self.connection_req_handler, QtCore.Qt.QueuedConnection)

    def connection_req_handler(self, req):
        if req == self.ConnectionRequest.CONNECT and self.connection_status == self.ConnectionStatus.DISCONNECTED:
            self.connection_status = self.ConnectionStatus.CONNECTING
            self.update_connection_status_signal.emit(self.connection_status)

        if req == self.ConnectionRequest.CANCEL and self.connection_status == self.ConnectionStatus.CONNECTING:
            self.connection_status = self.ConnectionStatus.DISCONNECTED
            self.update_connection_status_signal.emit(self.connection_status)
        
        if req == self.ConnectionRequest.DISCONNECT and self.connection_status == self.ConnectionStatus.CONNECTED:
            self.connection_status = self.ConnectionStatus.DISCONNECTED
            self.update_connection_status_signal.emit(self.connection_status)



