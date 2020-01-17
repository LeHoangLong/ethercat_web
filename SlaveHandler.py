import EthercatClient
import xml.etree.ElementTree as ET
import json

class SlaveHandler:
    def __init__(self, client, node_name, streamer):
        super().__init__()
        self.client = client
        self.client.addDataHandler(node_name, self.receive_handler)
        self.node_name = node_name
        self.type_list = []
        self.__getType()
        self.type_found = False
        self.streamer = streamer
        #self.streamer.addReceiveMessageHandler(self.streamerReceiveHandler)
        self.streamer.addReceiveControlHandler(self.node_name, self.streamerRxControlHandler)
        self.pending_control_from_streamer = {}
        self.pending_control_from_ethercat = {}
        
    def streamerRxControlHandler(self, message, reply):
        idx = message['idx']
        self.pending_control_from_streamer[idx] = reply
        root_node = ET.Element(self.node_name)
        control_val = message['value']
        control_node = ethercat_client.generateControl(control_val)
        root_node.append(control_node)
        self.client.sendToEthercat(root_node)


    def streamerReceiveHandler(self, received_dict):
        for node in received_dict:
            if node == self.node_name:
                root_node = ET.Element(self.node_name)
                message_list = node.value()
                for message_key in message_list:
                    if message_key == 'control':
                        control_list = message_list[message_key]
                        for control in control_list:
                            if (type(control) == str):
                                control_node = self.client.generateControl(control)
                            else:
                                control_dict = control
                                control_node = self.client.generateControl(control_dict['value'])
                            root_node.append(control_node)
                ET.dump(root_node)
                self.client.sendToEthercat(root_node)

    def getType(self):
        return self.type_list

    def __getType(self):
        root_node = ET.Element(self.node_name)
        control_node = self.client.generateControl('type')
        root_node.append(control_node)
        self.client.sendToEthercat(root_node)

    def receive_handler(self, node):
        if node.tag == self.node_name:
            json_dict = {self.node_name: []}
            for child in node:
                if child.tag == 'result':
                    result_dict = {
                        'type': child.tag,
                        'value': self.eTreeToDict(child)
                    }
                    json_dict[self.node_name].append(result_dict)
            self.streamer.sendMessage(json_dict)
            print(json.dumps(json_dict))

    def eTreeToDict(self, tree):
        ET.dump(tree)
        if 'value' in tree.attrib and tree.attrib['value'] == '[]':
            final_list = []
            for child in tree:
                final_list.append(self.eTreeToDict(child))
            return final_list
        else:
            if len(tree.getchildren()) == 0:
                if 'value' in tree.attrib:
                    return tree.attrib['value']
                else:
                    return tree.tag
            else:
                final_dict = {}
                if 'value' in tree.attrib:
                    final_dict['value'] = tree.attrib['value']
                for child in tree:
                    if child.tag != 'idx' and child.tag != 'value':
                        node_dict = self.eTreeToDict(child)
                        final_dict[child.tag] = node_dict
                return final_dict