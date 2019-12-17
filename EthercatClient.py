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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_name, server_port))
        self.control_idx = 0
        print("connected")
        connect_request = ET.Element('xml')
        dispatcher_server_node = ET.SubElement(connect_request, 'dispatcher_server')
        control_node = ET.SubElement(dispatcher_server_node, 'control')
        control_node.attrib['value'] = 'login'
        idx_node = ET.SubElement(control_node, "idx")
        idx_node.attrib['value'] = str(self.control_idx)
        source_node = ET.SubElement(control_node, 'source')
        source_node.attrib['value'] = 'host'
        username_node = ET.SubElement(control_node, 'username')
        username_node.attrib["value"] = 'test_username'
        password_node = ET.SubElement(control_node, 'password')
        password_node.attrib["value"] = 'test_password'
        
        self.socket.sendall(ET.tostring(connect_request) + b'\x00')
        replies = b""
        while b'\x00' not in replies:
            replies += self.socket.recv(1024)
            print("reply: " + str(replies))
        print('done receive')

        while replies.find(b'\x00') != -1:
            reply = replies[0:replies.find(b'\x00')]
            reply = ET.fromstring(reply)
            ET.dump(reply)
            for control in reply.findall('control'):
                for control_dest in control.getchildren():
                    if control_dest.tag == 'socket':
                        if control_dest.attrib['value'] == 'login':
                            result_node = control_dest.find('result')
                            if result_node == None or result_node.attrib['value'] != 'ok':
                                print(result_node)
                                print(result_node.attrib['value'])
                                print('close socket')
                                self.socket.close()
                            else:
                                print('connected')
            replies = replies[replies.find(b'\x00') + 1:]
        self.stop = False
        self.callback_map = {}
        
    def disconnect(self):
        command = ET.Element('xml')
        control = ET.SubElement(command, 'control')
        source = ET.SubElement(control, 'source')
        source.attrib["value"] = 'host'
        socket_control = ET.SubElement(control, 'socket')
        socket_control.attrib['value'] = 'disconnect'
        ET.dump(command)
        command = ET.tostring(command)
        self.socket.sendall(command + b'\x00')
        self.stop = True
        print('closed')

    def dataChannelHandler(self):
        data_string = b''
        while not self.stop:
            data_string += self.socket.recv(2048)
            self.data_packet = {}
            string_segment = b''
            for i in range(len(data_string)):
                c = data_string[i:i+1]
                if c == b'\0':
                    root = ET.fromstring(string_segment)
                    #ET.dump(root)
                    #root = message.find('xml')
                    for node in root:
                        source = node.tag
                        if source in self.callback_map:
                            self.callback_map[source](node)

                    string_segment = b''
                else:
                    string_segment += c
            data_string = string_segment
                        
        pass

    def sendToEthercat(self, node):
        message = ET.Element('xml')
        
        message.append(node)
        
        message = ET.tostring(message)
        self.socket.send(message)
        pass

    def run(self):
        threading.Thread(target=self.dataChannelHandler).start()

    def addDataHandler(self, node_name, callback):
        self.callback_map[node_name] = callback

    def generateControl(self, control_name):
        self.control_idx += 1
        control_element = ET.Element('control', attrib={'value':control_name})

        idx_node = ET.SubElement(control_element, 'idx')
        idx_node.attrib['value'] = str(self.control_idx)

        return control_element

def simulatedCallback(data_packet):
    print("callback")
    print(data_packet)


if __name__ == "__main__":        
    client = EthercatClient(server_name='localhost', server_port=1025)
    client.addDataHandler('test_node', simulatedCallback)
    client.run()
    time.sleep(2)
    client.disconnect()
    print('done')
