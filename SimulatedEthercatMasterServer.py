import socket
import xml.etree.ElementTree as ET
import sys
import threading
import random
import time

class SimulatedEthercatMasterServer():
    def __init__(self, *args, **kwargs):
        self.host_name = kwargs['hostname']
        self.port = kwargs['port']
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind((self.host_name, self.port))
        self.connection_counter = 1
        
    def run(self):
        print(self.host_name)
        print(self.port)
        self.listen_socket.listen()
        print('listening')
        while True:
            conn, addr = self.listen_socket.accept()
            print('accepted')
            connection_request = conn.recv(1024)
            print(connection_request)
            connect_request = ET.fromstring(connection_request)
            connect_request_reply = ET.Element('iq')
            for query in connect_request.findall('query'):
                query.set('type', 'result')
                query.attrib.pop('username')
                query.attrib.pop('password')
                ET.SubElement(query, 'item', {'channel': 'data', 'hostname': self.host_name, 'port':str(self.port + self.connection_counter)})
                ET.SubElement(query, 'item', {'channel': 'control', 'hostname': self.host_name, 'port':str(self.port + self.connection_counter + 1)})
                ET.SubElement(query, 'item', {'channel': 'emergency', 'hostname': self.host_name, 'port':str(self.port + self.connection_counter + 2)})
                new_data_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_data_channel.bind((self.host_name, self.port + self.connection_counter))
                new_data_channel.setblocking(True)
                new_data_channel.listen()
                new_control_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_control_channel.bind((self.host_name, self.port + self.connection_counter + 1))
                new_control_channel.setblocking(True)
                new_control_channel.listen()
                new_emergency_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_emergency_channel.bind((self.host_name, self.port + self.connection_counter + 2))
                new_emergency_channel.setblocking(True)
                new_emergency_channel.listen()
                client_handler = clientHandler(new_data_channel, new_control_channel, new_emergency_channel)
                client_handler.run()
                self.connection_counter += 3
                connect_request_reply.append(query)
            ET.dump(connect_request_reply)
            conn.sendall(ET.tostring(connect_request_reply))
            conn.close()

class clientHandler():
    def __init__(self, data_channel, control_channel, emergency_channel):
        self.data_channel = data_channel
        self.control_channel = control_channel
        self.emergency_channel = emergency_channel
        self.stop = False
        self.mean_speed = 1

    def run(self):
        self.stop = False
        threading.Thread(target=self.dataChannelHandler, args=()).start()
        threading.Thread(target=self.controlChannelHandler, args=()).start()
        threading.Thread(target=self.emergencyChannelHandler, args=()).start()

        

    def dataChannelHandler(self):
        conn, addr = self.data_channel.accept()
        data_1 = 0
        while not self.stop:
            data_2 = random.random() + self.mean_speed
            data_1 += self.mean_speed
            message = ET.Element('data')
            time_element = ET.SubElement(message, 'item')
            time_element.text = str(time.time() * 1000)
            time_element.attrib['type'] = 'time'
            data_element = ET.SubElement(message, 'item')
            data_element.text = str(data_1)
            data_element.attrib['type'] = 'sensor1'
            data_element = ET.SubElement(message, 'item')
            data_element.text = str(data_2)
            data_element.attrib['type'] = 'sensor2'
            message = ET.tostring(message) + b'\0'
            #print(message)
            conn.sendall(message)
            time.sleep(0.1)
        close_message = ET.Element('close')
        close_message = ET.tostring(close_message)
        conn.sendall(close_message)
        self.data_channel.close()
        print('data channel stopped')


    def controlChannelHandler(self):
        conn, addr = self.control_channel.accept()
        while not self.stop:
            message = conn.recv(1024)
            #print(message)
            message = ET.fromstring(message)
            for command in message.findall('value'):
                print(command.text)
                if command.text == 'stop':
                    self.stop = True
                    print('stopped')
                if command.attrib['to'] == 'motor':
                    if command.text == 'decelerate':
                        self.mean_speed -= 1
                    elif command.text == 'accelerate':
                        self.mean_speed += 1

        self.control_channel.close()
        print('control channel stopped')

    
    def emergencyChannelHandler(self):
        while not self.stop:
            pass
        self.emergency_channel.close()
        print('emergency channel stopped')

if __name__ == "__main__":
    server = SimulatedEthercatMasterServer(hostname='localhost', port=1025)
    server.run()