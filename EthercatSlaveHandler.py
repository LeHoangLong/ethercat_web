import EthercatClient
import xml.etree.ElementTree as ET

class EthercatSlaveHandler:
    def __init__(self, ethercat_client, node_name):
        ethercat_client.addDataHandler(node_name, self.receive_handler)
        self.ethercat_client = ethercat_client
        self.message_handler = []
        self.node_name = node_name

    def receive_handler(self, node):
        message_dict_list = []
        for child in node:
            if child.tag == 'message':
                message_dict = {}
                if child.attrib['value'] == 'pdo':
                    message_dict['source'] = 'unknown'
                    message_dict['time'] = '0'
                    message_dict['value'] = child.attrib['value']
                    for grandchild in child:
                        if grandchild.tag == 'source':
                            message_dict[grandchild.tag] = grandchild.attrib['value']
                        elif grandchild.tag == 'time':
                            message_dict[grandchild.tag] = grandchild.attrib['value']
                        elif grandchild.tag == 'data':
                            message_dict[grandchild.tag] = {}
                            for data in grandchild:
                                message_dict[grandchild.tag][data.tag] = data.attrib['value']
                    #receive pdo handler
                message_dict_list.append(message_dict)

        if len(message_dict_list) > 0:
            for handler in self.message_handler:
                handler(message_dict_list)

    def addMessageHandler(self, handler):
        self.message_handler.append(handler)

    def sendMessage(self, message):
        for node_message in message:
            if 'dest' in node_message.keys() and node_message['dest'] == self.node_name:
                #only process if there is a destination node
                root_node = ET.Element(node_message['dest'])
                for child in node_message:
                    message_node = ET.SubElement(root_node, 'message')
                    message_node.attrib['value'] = child['value']
                    if 'time' in child.keys():
                        time_node = ET.SubElement(root_node, 'time')
                        time_node.attrib['value'] = child['time']
                    if 'source' in child.keys():
                        message_node = ET.SubElement(root_node, 'source')
                        message_node.attrib['value'] = child['source']
                    if 'data' in child.keys():
                        data_node = ET.SubElement(root_node, 'data')
                        for data_element_name in child['data']:
                            data_element_node = ET.SubElement(data_node, data_element_name)
                            data_element_node.attrib['value'] = child['data'][data_element_name]
                self.ethercat_client.sendToEthercat(root_node)

        pass

    def sendControl(self, control):
        pass