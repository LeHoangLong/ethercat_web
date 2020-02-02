from enum import Enum
from PyQt5 import QtWidgets, QtCore

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DictionaryDataStreamer import DictionaryDataStreamer

class AppBackend(QtCore.QObject):
    presence_updated_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.streamer = DictionaryDataStreamer(name='long_2', domain='long-inspiron-5447',\
            password='123')
        self.streamer.connect(block=True)
        self.workstation_list = []
        self.streamer.addPresenceUpdateHandler(self.presenceUpdateHandler)

    def createWorkstationBackend(self, workstation_address):
        return WorkstationBackend(workstation_address, self.streamer)

    def getWorkstationList(self):
        return self.streamer.getListOfPeers()

    def presenceUpdateHandler(self, peer_list):
        self.presence_updated_signal.emit()

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
    all_node_received_signal = QtCore.pyqtSignal(list)
    node_type_received = QtCore.pyqtSignal(str, list)
    available_collect_data_update = QtCore.pyqtSignal(list)

    def __init__(self, workstation_address, streamer, parent=None):
        super().__init__(parent)
        self.node_list = []
        self.address = workstation_address
        self.streamer = streamer
        self.connection_status = self.ConnectionStatus.DISCONNECTED
        self.connection_req.connect(self.connection_req_handler, QtCore.Qt.QueuedConnection)
        self.streamer.addReceiveMessageHandler(self.receiveMessageHandler)
        self.streamer.addPresenceUpdateHandler(self.presenceUpdateHandler)
        self.getAllNodes()

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

    def getAllNodes(self):
        get_node_request = {'node': 'list_of_nodes', 'type': 'control', 'value': 'get'}
        self.streamer.sendControl('list_of_nodes', 'get', reply_handler=self.listOfNodeReplyReceiveHandler)

    def getAvailableCollectData(self, node_name):
        available_data = []
        if node_name == 'test_node':
            available_data = ['data_1', 'data_2']
        self.available_collect_data_update.emit(available_data)

    def listOfNodeReplyReceiveHandler(self, reply):
        self.node_list = reply['return']['nodes']
        self.all_node_received_signal.emit(self.node_list)

    def sendControl(self, node_name, command, reply_handler=None):
        if node_name in self.node_list:
            self.streamer.sendControl(node_name, command, reply_handler=reply_handler)
        
    def getNodeType(self, node_name):
        if node_name in self.node_list:
            self.streamer.sendControl(node_name, 'type', reply_handler=self.typeReceiveHandler)

    def typeReceiveHandler(self, reply):
        type_list = reply['return']['types']
        self.node_type_received.emit(reply['node'], type_list)

    def receiveMessageHandler(self, message_list):
        for message in message_list:
            if message['node'] == 'list_of_nodes':
                if message['type'] == 'reply':
                    pass
        pass

    def presenceUpdateHandler(self, peer_list):
        pass