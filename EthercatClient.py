import socket
import xml.etree.ElementTree as ET
import sys
import threading
import time
import sleekxmpp
from sleekxmpp import ClientXMPP
import msgpack

class EthercatClient():
    def __init__(self, *args, **kwargs):
        server_name = kwargs['server_name']
        server_port = kwargs['server_port']
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_name, server_port))
        connect_request = ET.Element('iq')
        query_attr = {'type': 'get', 'value': 'new-connection', 'username': 'admin', 'password': '1234'}
        ET.SubElement(connect_request, 'query', query_attr)
        server_socket.sendall(ET.tostring(connect_request))
        reply = server_socket.recv(1024)
        reply = ET.fromstring(reply)
        ET.dump(reply)
        for query in reply.findall('query'):
            for item in query.findall('item'):
                if item.attrib['channel'] == 'data':
                    data_server_port = int(item.attrib['port'])
                    data_server_name = item.attrib['hostname']
                    self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.data_socket.connect((data_server_name, data_server_port))
                elif item.attrib['channel'] == 'control':
                    control_server_port = int(item.attrib['port'])
                    control_server_name = item.attrib['hostname']
                    self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.control_socket.connect((control_server_name, control_server_port))
                elif item.attrib['channel'] == 'emergency':
                    emergency_server_port = int(item.attrib['port'])
                    emergency_server_name = item.attrib['hostname']
                    self.emergency_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.emergency_socket.connect((emergency_server_name, emergency_server_port))
        server_socket.close()
        self.stop = False
        self.callback_list = []

    def disconnect(self):
        command = ET.Element('cmd')
        disconnect_command = ET.SubElement(command, 'value')
        disconnect_command.text = 'stop'
        command = ET.tostring(command)
        self.control_socket.sendall(command)
        self.stop = True
        self.control_socket.close()
        self.emergency_socket.close()
        print('closed')

    def dataChannelHandler(self):
        data_string = b''
        while not self.stop:
            data_string += self.data_socket.recv(2048)
            self.data_packet = {}
            string_segment = b''
            for i in range(len(data_string)):
                c = data_string[i:i+1]
                if c == b'\0':
                    message = ET.fromstring(string_segment)
                    if message.tag == 'data':
                        for item in message.findall('item'):
                            self.data_packet[item.attrib['type']] = item.text
                            for callback in self.callback_list:
                                callback(self.data_packet)    
                    elif message.tag == 'close':
                        self.data_socket.close()
                    string_segment = b''
                else:
                    string_segment += c
            data_string = string_segment
                        
        pass

    def sendToEthercat(self, node_name, command):
        message = ET.Element('cmd')
        cmd = ET.SubElement(message, 'value', {'to': node_name})
        cmd.text = command
        message = ET.tostring(message)
        self.control_socket.send(message)
        pass

    def run(self):
        threading.Thread(target=self.dataChannelHandler).start()

    def addDataHandler(self, callback):
        self.callback_list.append(callback)

def simulatedCallback(data_packet):
    print(data_packet)


if __name__ == "__main__":        
    client = EthercatClient(server_name='localhost', server_port=1025)
    client.addDataHandler(simulatedCallback)
    client.run()
    time.sleep(1)
    client.disconnect()
    print('done')
