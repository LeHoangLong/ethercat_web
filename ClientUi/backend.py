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
from Trigger import *

class AppBackend(QtCore.QObject):
    presence_updated_signal = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.streamer = DictionaryDataStreamer(name='long_2', domain='long-inspiron-5447',\
        #    password='123')
        self.streamer = DictionaryDataStreamer(name='long_2', domain='34.87.175.118',\
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
        
        self.start_trigger_map = {}
        self.start_comparator_list = []
        self.end_trigger_map = {}
        self.end_comparator_list = []

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

        self.streamer.addReceiveMessageHandler(self.programStateReceiveHandler)

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
        available_data = []
        if node_name == "test_node":
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
        elif node_name == "motor_1":
            available_data = [
                {
                    'name': 'current_motor_profile',
                    'type': 'list',
                    'data': [
                        {
                            'name': 'feedback_acceleration',
                            'type': 'float'
                        },
                        {
                            'name': 'feedback_velocity',
                            'type': 'float'
                        },
                        {
                            'name': 'feedback_position',
                            'type': 'float'
                        },
                        {
                            'name': 'motor_status',
                            'type': 'int'
                        }
                    ]
                }
            ]
        elif node_name == 'program':
            available_data = [
                {
                    'name': 'program_states',
                    'type': 'list',
                    'data': [
                        {
                            'name': 'run_counter',
                            'type': 'int'
                        }
                    ]
                }
            ]
        return available_data

    def setSaveLocation(self, path):
        self.save_path = path
        self.current_file_idx = 0
        self.current_file_length = 0

    def startTriggerHandler(self):
        if self.is_collecting_data == False:
            self.startDataCollection()
        pass

    def endTriggerHandler(self):
        if self.is_collecting_data:
            if (self.current_file == None or self.current_file_length > 3) and self.save_path != None:
                if len(self.collected_data_list) > 0 and self.current_file != None:
                    self.current_file.write(json.dumps(self.collected_data_list))
                    self.collected_data_list = []
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

    def clearTrigger(self, trigger_type):
        if trigger_type == 'START_TRIGGER':
            self.start_trigger_map = {}
            self.start_comparator_list = []
        if trigger_type == 'END_TRIGGER':
            self.end_trigger_map = {}
            self.end_comparator_list = []

    def addTrigger(self, trigger_info, trigger_type):
        if trigger_type == 'START_TRIGGER':
            if trigger_info['condition_A'] not in self.start_trigger_map:
                self.start_trigger_map[trigger_info['condition_A']] = {}
                self.start_trigger_map[trigger_info['condition_A']]['data_type'] = trigger_info['condition_A_type']
                self.start_trigger_map[trigger_info['condition_A']]['trigger'] = []
            trigger_1 = self.__createTriggerHandler(trigger_info['condition_A'])
            self.start_trigger_map[trigger_info['condition_A']]['trigger'].append(trigger_1)

            if trigger_info['condition_B'] not in self.start_trigger_map:
                self.start_trigger_map[trigger_info['condition_B']] = {}
                self.start_trigger_map[trigger_info['condition_B']]['data_type'] = trigger_info['condition_B_type']
                self.start_trigger_map[trigger_info['condition_B']]['trigger'] = []
            trigger_2 = self.__createTriggerHandler(trigger_info['condition_B'])
            self.start_trigger_map[trigger_info['condition_B']]['trigger'].append(trigger_2)

            self.start_comparator_list.append(Comparator(trigger_info['comparison'], trigger_1, trigger_2))
        
        elif trigger_type == 'END_TRIGGER':
            if trigger_info['condition_A'] not in self.end_trigger_map:
                self.end_trigger_map[trigger_info['condition_A']] = {}
                self.end_trigger_map[trigger_info['condition_A']]['data_type'] = trigger_info['condition_A_type']
                self.end_trigger_map[trigger_info['condition_A']]['trigger'] = []
            trigger_1 = self.__createTriggerHandler(trigger_info['condition_A'])
            self.end_trigger_map[trigger_info['condition_A']]['trigger'].append(trigger_1)

            if trigger_info['condition_B'] not in self.end_trigger_map:
                self.end_trigger_map[trigger_info['condition_B']] = {}
                self.end_trigger_map[trigger_info['condition_B']]['data_type'] = trigger_info['condition_B_type']
                self.end_trigger_map[trigger_info['condition_B']]['trigger'] = []
            trigger_2 = self.__createTriggerHandler(trigger_info['condition_B'])
            self.end_trigger_map[trigger_info['condition_B']]['trigger'].append(trigger_2)
            
            self.end_comparator_list.append(Comparator(trigger_info['comparison'], trigger_1, trigger_2))
        

    def __createTriggerHandler(self, condition_name):
        if condition_name == '/Number of samples':
            return NumberOfSamplesTrigger()
        elif condition_name.split(':')[0] == '/Constant':
            return ConstantTrigger(float(condition_name.split(':')[1]))
        else:
            return ValueTrigger()
    
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
                        'collector_list': [],
                        'trigger_handler_list': []
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
        if self.data_collection_enabled:
            data_list = []
            prefix = '/' + message['node'] + '/' + message['value']

            if '/Number of samples' in self.start_trigger_map:
                trigger_list = self.start_trigger_map['/Number of samples']
                for trigger in trigger_list:
                    trigger.updateData(0)

            if '/Number of samples' in self.end_trigger_map:
                trigger_list = self.end_trigger_map['/Number of samples']
                for trigger in trigger_list:
                    trigger.updateData(0)

            if 'time' in message:
                time = int(message['time'])
            else:
                time = None
            self.extractDataFromMessage(time, message['data'], data_list, prefix)
            
            condition_met = len(self.start_comparator_list) > 0
            for start_comparator in self.start_comparator_list:
                start_comparator.compare()
                if not start_comparator.isConditionMet():
                    condition_met = False
                    break
            if condition_met:
                self.startTriggerHandler()
                for start_comparator in self.start_comparator_list:
                    start_comparator.reset()

            condition_met = len(self.end_comparator_list) > 0
            for end_comparator in self.end_comparator_list:
                end_comparator.compare()
                if not end_comparator.isConditionMet():
                    condition_met = False
                    break
            if condition_met:
                self.endTriggerHandler()
                for end_comparator in self.end_comparator_list:
                    end_comparator.reset()

    def extractDataFromMessage(self, time, data_dict, extracted_list, prefix=None):
        for data_name in data_dict:
            if isinstance(data_dict[data_name], dict):
                path = prefix + '/' + data_name
                self.extractDataFromMessage(time, data_dict[data_name], extracted_list, path)
            else:
                full_name = prefix + '/' + data_name

                if full_name in self.start_trigger_map:
                    trigger_list = self.start_trigger_map[full_name]['trigger']
                    type_str = self.start_trigger_map[full_name]['data_type']
                    data = None
                    if type_str == 'int':
                        data = int(data_dict[data_name])
                    elif type_str == 'float':
                        data = float(data_dict[data_name])
                    for trigger in trigger_list:
                        trigger.updateData(data)

                if full_name in self.end_trigger_map:
                    trigger_list = self.end_trigger_map[full_name]['trigger']
                    type_str = self.end_trigger_map[full_name]['data_type']
                    data = None
                    if type_str == 'int':
                        data = int(data_dict[data_name])
                    elif type_str == 'float':
                        data = float(data_dict[data_name])
                    for trigger in trigger_list:
                        trigger.updateData(data)

                if full_name in self.data_collector_list:
                    collector_map = self.data_collector_list[full_name]
                    type_str = collector_map['data_type']
                    data = None
                    if type_str == 'int':
                        data = int(data_dict[data_name])
                    elif type_str == 'float':
                        data = float(data_dict[data_name])
                    if data != None:
                        if self.is_collecting_data:
                            print(data)
                            collector_map['data'].append(data)
                    
                if full_name in self.data_watch_map:
                    watcher_list = self.data_watch_map[full_name]['handler']
                    data_type = self.data_watch_map[full_name]['data_type']
                    data = None
                    if data_type == 'int':
                        data = int(data_dict[data_name])
                    elif data_type == 'float':
                        data = float(data_dict[data_name])

                    for watcher in watcher_list:
                        watcher(data, time, data_type)

    def presenceUpdateHandler(self, peer_list):
        pass

    def sendControlSignal(self, control_signal_name, value=''):
        param = {
            control_signal_name: value
        }
        self.streamer.sendControl('program', 'set', param=param, reply_handler=self.programStateReceiveHandler)

    def programStateReceiveHandler(self, message):
        if message['node'] == 'program':
            if message['type'] == 'return':
                return_node = message['return']
                self.program_state = return_node['states']
                self.program_state_updated_signal.emit()
            elif message['type'] == 'message':
                data_node = message['data']
                self.program_state = data_node['states']
                self.program_state_updated_signal.emit()

    def getProgramState(self):
        return self.program_state

    def __updateProgramState(self):
        while True:
            self.streamer.sendControl('program', 'get_states', reply_handler=self.programStateReceiveHandler)
            time.sleep(1)

    def addDataWatch(self, data_watcher_handler, data_name, data_type):
        if data_name not in self.data_watch_map:
            self.data_watch_map[data_name] = {
                'handler': [],
                'data_type': data_type
            }
        
        if data_watcher_handler not in self.data_watch_map[data_name]['handler']:
            self.data_watch_map[data_name]['handler'].append(data_watcher_handler)

    def removeDataWatch(self, watcher_to_remove):
        if watcher_to_remove != None:
            for data_watch_map_name, watcher_list_and_data_type in self.data_watch_map.items():
                watcher_list = watcher_list_and_data_type['handler']
                for watcher in watcher_list:
                    if watcher == watcher_to_remove:
                        watcher_list.remove(watcher)
                        break
            self.data_watch_map = {k : v for k,v in self.data_watch_map.items() if len(v['handler']) > 0}


