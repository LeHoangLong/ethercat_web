from enum import Enum
from PyQt5 import QtWidgets, QtCore
import numpy as np

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

class DataCollector:
    def __init__(self):

        pass

    def addDataPoint(self, data, time=None):
        pass

    def getDataToStore(self):
        return None

    def resetSample(self):
        pass


class MeanDataCollector(DataCollector):
    def __init__(self):
        super().__init__()
        self.samples = []
        pass

    def addDataPoint(self, data, time=None):
        self.samples.append(data)

    def getDataToStore(self):
        array = np.asarray(self.samples)
        return np.mean(array)

    def resetSample(self):
        self.samples = []

class NumberOfSamplesTrigger():
    def __init__(self):
        self.sample_count = 0

    def updateData(self, data):
        self.sample_count += 1
    
    def getValue(self):
        return self.sample_count

    def reset(self):
        self.sample_count = 0

class ConstantTrigger():
    def __init__(self, value):
        self.value = value
        pass

    def updateData(self, data):
        pass

    def getValue(self):
        return self.value

    def reset(self):
        pass

class Comparator():
    def __init__(self, comparison_type, callback):
        self.comparison_type = comparison_type
        self.callback = callback

    def compare(self, value_1, value_2):
        condition_met = False
        if self.comparison_type == '>':
            if value_1 > value_2:
                condition_met = True

        if condition_met and self.callback != None:
            self.callback()

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
        self.data_collector_list = {}
        self.is_collecting_data = False
        self.trigger_count = 0
        self.condition_A = {
            'name': '',
            'obj': None
        }
        self.condition_B = {
            'name': '',
            'obj': None
        }
        self.comparator = None

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

    def getAvailableCollectData(self):
        available_data = [
            {
                'name': 'pdo',
                'type': 'list',
                'data': [
                    {
                        'name': 'test_data',
                        'type': 'int'
                    }
                ]
            },
        ]
        return available_data

    def createTriggerHandler(self, condition_name):
        if condition_name == 'Number of samples':
            return NumberOfSamplesTrigger()
        elif condition_name.split(':')[0] == 'Constant':
            return ConstantTrigger(float(condition_name.split(':')[1]))

    def startTriggerHandler(self):
        self.condition_A['obj'].reset()
        self.condition_B['obj'].reset()
        pass

    def addTrigger(self, condition_A, condition_B, comparison_type, trigger_type):
        self.condition_A['name'] = condition_A
        self.condition_A['obj'] = self.createTriggerHandler(condition_A)
        self.condition_B['name'] = condition_B
        self.condition_B['obj'] = self.createTriggerHandler(condition_B)
        if trigger_type == 'START_TRIGGER':
            self.comparator = Comparator(comparison_type, self.startTriggerHandler)
        pass
        

    def addDataCollector(self, data_name, collect_type, data_type):
        collector_existed = False

        if data_name in self.data_collector_list:
            for collector_map in self.data_collector_list[data_name]: 
                if collector_map['collect_type'] == collect_type:
                    collector_existed = True

        if collector_existed == False:
            data_collector = None
            if collect_type == 'DEFAULT':
                data_collector = MeanDataCollector()

            if data_collector != None:
                collector_map = {
                    'collector': data_collector,
                    'collect_type': collect_type
                }
                
                if data_name not in self.data_collector_list:
                    self.data_collector_list[data_name] = {
                        'data_type': data_type,
                        'data': [],
                        'collector_list': []
                    }

                self.data_collector_list[data_name]['collector_list'].append(collector_map)
                    
            return True
        else:
            return False

    def startDataCollection(self):
        self.is_collecting_data = True
    
    def stopDataCollection(self):
        self.is_collecting_data = False

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

    def receiveMessageHandler(self, message):
        #extract data and name
        data_list = []
        prefix = message['node'] + '/' + message['value']
        self.extractDataFromMessage(message['data'], data_list, prefix)

        if self.condition_A['name'] == 'Number of samples' or self.condition_A['name'] == 'Constant':
            self.condition_A['obj'].updateData(0)
        if self.condition_B['name'] == 'Number of samples' or self.condition_B['name'] == 'Constant':
            self.condition_B['obj'].updateData(0)
        if self.comparator != None and self.condition_A['obj'] != None and self.condition_B['obj'] != None:
            self.comparator.compare(self.condition_A['obj'].getValue(), self.condition_B['obj'].getValue())
        

    def extractDataFromMessage(self, data_dict, extracted_list, prefix=None):
        for data_name in data_dict:
            if isinstance(data_dict[data_name], dict):
                path = prefix + '/' + data_name
                self.extractDataFromMessage(data_dict[data_name], extracted_list, path)
            else:
                full_name = prefix + '/' + data_name
                 
                if full_name in self.data_collector_list:
                    collector_map = self.data_collector_list[full_name]
                    type_str = collector_map['data_type']
                    data = None
                    if type_str == 'int':
                        data = int(data_dict[data_name])
                    if data != None:
                        collector_map['data'].append(data)
                        if full_name == self.condition_A['name']:
                            self.condition_A['obj'].updateData(data)
                        if full_name == self.condition_B['name']:
                            self.condition_B['obj'].updateData(data)

    def presenceUpdateHandler(self, peer_list):
        pass