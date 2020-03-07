from enum import Enum
from PyQt5 import QtWidgets, QtCore
import numpy as np
from sklearn import linear_model
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DictionaryDataStreamer import DictionaryDataStreamer
from threading import Thread
import time

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

    def getValue(self, data):
        return np.mean(data)

class InterpolateDataCollector(DataCollector):
    def __init__(self):
        super().__init__()
        pass

    def getValue(self, data):
        return_dict = {}
        lm = linear_model.LinearRegression()
        x_axis = np.arange(data.size)
        x_axis = np.expand_dims(x_axis, axis=1)
        model = lm.fit(x_axis, data)
        model_coef_list = model.coef_.tolist()
        for i, coeff in enumerate(model_coef_list):
            return_dict['gradient_' + str(i)] = coeff
        return_dict['intercept'] = model.intercept_
        return return_dict

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

class ValueTrigger():
    def __init__(self):
        self.data = 0
        pass

    def updateData(self, data):
        self.data = data
        pass

    def getValue(self):
        return self.data

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
        elif self.comparison_type == '>=':
            if value_1 >= value_2:
                condition_met = True
        elif self.comparison_type == '==':
            if value_1 == value_2:
                condition_met = True
        elif self.comparison_type == '!=':
            if value_1 != value_2:
                condition_met = True
        elif self.comparison_type == '<=':
            if value_1 <= value_2:
                condition_met = True
        elif self.comparison_type == '<':
            if value_1 < value_2:
                condition_met = True

        if condition_met and self.callback != None:
            self.callback()
            return True
        else:
            return False

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
    program_state_updated_signal = QtCore.pyqtSignal()
   
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
        self.sample_count = 0
        self.start_condition_A = {
            'name': '',
            'obj': None
        }
        self.start_condition_B = {
            'name': '',
            'obj': None
        }
        self.end_condition_A = {
            'name': '',
            'obj': None
        }
        self.end_condition_B = {
            'name': '',
            'obj': None
        }
        self.start_comparator = None
        self.end_comparator = None
        self.save_path = None
        self.current_file = None
        self.current_file_idx = 0
        self.current_file_length = 0
        self.watcher_counter = 0
        self.collected_data_list = []
        self.data_collection_enabled = False
        self.program_state = {}
        self.data_watch_map = {}
        self.thread = Thread(target=self.__updateProgramState)
        self.thread.start()

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
        self.streamer.sendControl('list_of_nodes', 'get', reply_handler=self.listOfNodeReplyReceiveHandler)

    def getAvailableCollectData(self, node_name):
        available_data = [
            {
                'name': 'rx_pdo',
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

    def setSaveLocation(self, path):
        self.save_path = path
        self.current_file_idx = 0
        self.current_file_length = 0

    def createTriggerHandler(self, condition_name):
        if condition_name == '/Number of samples':
            return NumberOfSamplesTrigger()
        elif condition_name.split(':')[0] == '/Constant':
            return ConstantTrigger(float(condition_name.split(':')[1]))
        else:
            return ValueTrigger()

    def startTriggerHandler(self):
        if self.is_collecting_data == False:
            self.startDataCollection()
        pass

    def endTriggerHandler(self):
        if self.is_collecting_data:
            if (self.current_file == None or self.current_file_length > 3) and self.save_path != None:
                if len(self.collected_data_list) > 0 and self.current_file != None:
                    self.current_file.write(json.dumps(self.collected_data_list))
                if self.save_path != '':
                    self.current_file = open(self.save_path + '/collected_data_' + str(self.current_file_idx), 'w')
                else:
                    self.current_file = open('.' + '/collected_data_' + str(self.current_file_idx), 'w')
                self.current_file_length = 0
                self.current_file_idx += 1
            self.stopDataCollection()
            current_collect_data = {}
            if self.current_file != None:
                print('sample_' + str(self.sample_count) + ':')
                current_collect_data['sample_number'] = self.sample_count
                #self.current_file.write('sample_number: ' + str(self.sample_count) + '\n\t')
            for data_name in self.data_collector_list:
                #print(data_name)
                collected_data_map = self.data_collector_list[data_name]
                collector_list = collected_data_map['collector_list']
                collected_data = collected_data_map['data']
                #print(collected_data_map)
                collected_data = np.asarray(collected_data)
                for collector in collector_list:
                    val = collector['collector'].getValue(collected_data)
                    if self.current_file != None:
                        #print(data_name + ': ' + str(val))
                        #self.current_file.write(data_name + '_' + collected_data_map['collector_type'] + ': ' + str(val) + '\n')
                        if isinstance(val, (dict)):
                            for val_name, val_value in val.items():
                                current_collect_data[data_name + '_' + collector['collect_type'] + '/' + val_name] = val_value
                        else:
                            current_collect_data[data_name + '_' + collector['collect_type']] = val
                        self.current_file_length += 1
                        self.sample_count += 1
                collected_data_map['data'] = []
            if len(current_collect_data) > 1:
                self.collected_data_list.append(current_collect_data)

    def setTrigger(self, condition_A, condition_B, comparison_type, trigger_type):
        if trigger_type == 'START_TRIGGER':
            self.start_condition_A['name'] = condition_A
            self.start_condition_A['obj'] = self.createTriggerHandler(condition_A)
            self.start_condition_B['name'] = condition_B
            self.start_condition_B['obj'] = self.createTriggerHandler(condition_B)
            self.start_comparator = Comparator(comparison_type, self.startTriggerHandler)
        elif trigger_type == 'END_TRIGGER':
            self.end_condition_A['name'] = condition_A
            self.end_condition_A['obj'] = self.createTriggerHandler(condition_A)
            self.end_condition_B['name'] = condition_B
            self.end_condition_B['obj'] = self.createTriggerHandler(condition_B)
            self.end_comparator = Comparator(comparison_type, self.endTriggerHandler)
        pass

    def setCollector(self, collector_list):
        self.data_collector_list = {}
        for collector_info in collector_list:
            self.addDataCollector(collector_info['data_name'], collector_info['collector_type'], collector_info['data_type'])
        pass
        
    def getSupportedCollectorType(self):
        return ['MEAN', "LINEAR_INTERPOLATION"]

    def addDataCollector(self, data_name, collect_type, data_type):
        collector_existed = False

        if data_name in self.data_collector_list:
            for collector_map in self.data_collector_list[data_name]: 
                if collector_map['collect_type'] == collect_type:
                    collector_existed = True

        if collector_existed == False:
            data_collector = None
            if collect_type == 'MEAN':
                data_collector = MeanDataCollector()
            else:
                data_collector = InterpolateDataCollector()

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

    def enableDataCollection(self):
        self.data_collection_enabled = True

    def disableDataCollection(self):
        self.data_collection_enabled = False

    def startDataCollection(self):
        if self.data_collection_enabled:
            self.is_collecting_data = True
    
    def stopDataCollection(self):
        if self.data_collection_enabled:
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
        #print('enable: ' + str(self.data_collection_enabled))
        #print('collecting: ' + str(self.is_collecting_data))
        if self.data_collection_enabled:
            data_list = []
            prefix = '/' + message['node'] + '/' + message['value']
            if self.start_condition_A['name'] == '/Number of samples' or self.start_condition_A['name'] == '/Constant':
                self.start_condition_A['obj'].updateData(0)
            if self.start_condition_B['name'] == '/Number of samples' or self.start_condition_B['name'] == '/Constant':
                self.start_condition_B['obj'].updateData(0)
            
            if self.end_condition_A['name'] == '/Number of samples' or self.end_condition_A['name'] == '/Constant':
                self.end_condition_A['obj'].updateData(0)
            if self.end_condition_B['name'] == '/Number of samples' or self.end_condition_B['name'] == '/Constant':
                self.end_condition_B['obj'].updateData(0)
            
            if 'time' in message:
                time = message['time']
            else:
                time = None
            self.extractDataFromMessage(time, message['data'], data_list, prefix)

    def extractDataFromMessage(self, time, data_dict, extracted_list, prefix=None):
        for data_name in data_dict:
            if isinstance(data_dict[data_name], dict):
                path = prefix + '/' + data_name
                self.extractDataFromMessage(time, data_dict[data_name], extracted_list, path)
            else:
                full_name = prefix + '/' + data_name
                if full_name in self.data_collector_list:
                    collector_map = self.data_collector_list[full_name]
                    type_str = collector_map['data_type']
                    data = None
                    if type_str == 'int':
                        data = int(data_dict[data_name])
                    if data != None:
                        if self.start_condition_A['obj'] != None and full_name == self.start_condition_A['name']:
                            self.start_condition_A['obj'].updateData(data)
                        if self.start_condition_B['obj'] != None and full_name == self.start_condition_B['name']:
                            self.start_condition_B['obj'].updateData(data)
                        if self.end_condition_A['obj'] != None and full_name == self.end_condition_A['name']:
                            self.end_condition_A['obj'].updateData(data)
                        if self.end_condition_B['obj'] != None and full_name == self.end_condition_B['name']:
                            self.end_condition_B['obj'].updateData(data)
                        
                        if self.start_comparator != None and self.start_condition_A['obj'] != None and self.start_condition_B['obj'] != None:
                            if self.start_comparator.compare(self.start_condition_A['obj'].getValue(), self.start_condition_B['obj'].getValue()):
                                self.start_condition_A['obj'].reset()
                                self.start_condition_B['obj'].reset()
        
                        if self.end_comparator != None and self.end_condition_A['obj'] != None and self.end_condition_B['obj'] != None:
                            if self.end_comparator.compare(self.end_condition_A['obj'].getValue(), self.end_condition_B['obj'].getValue()):
                                self.end_condition_A['obj'].reset()
                                self.end_condition_B['obj'].reset()
                    
                        if self.is_collecting_data:
                            collector_map['data'].append(data)
                        pass
                    
                if full_name in self.data_watch_map:
                    watcher_list = self.data_watch_map[full_name]
                    for watcher in watcher_list:
                        watcher(data_dict[data_name], time)

    def presenceUpdateHandler(self, peer_list):
        pass

    def sendControlSignal(self, control_signal_name, value=''):
        param = {
            control_signal_name: value
        }
        self.streamer.sendControl('program', 'set', param=param, reply_handler=self.programStateReceiveHandler)

    def programStateReceiveHandler(self, message):
        return_node = message['return']
        self.program_state = return_node['states']
        self.program_state_updated_signal.emit()

    def getProgramState(self):
        return self.program_state

    def __updateProgramState(self):
        while True:
            self.streamer.sendControl('program', 'get_states', reply_handler=self.programStateReceiveHandler)
            time.sleep(1)

    def addDataWatch(self, data_watcher_handler, data_name):
        if data_name not in self.data_watch_map:
            self.data_watch_map[data_name] = []
        
        if data_watcher_handler not in self.data_watch_map[data_name]:
            self.data_watch_map[data_name].append(data_watcher_handler)

    def removeDataWatch(self, watcher_to_remove):
        if watcher_to_remove != None:
            for data_watch_map_name, watcher_list in self.data_watch_map.items():
                for watcher in watcher_list:
                    if watcher == watcher_to_remove:
                        watcher_list.remove(watcher)
                        break
                if len(watcher_list) == 0:
                    del self.data_watch_map[data_watch_map_name]


