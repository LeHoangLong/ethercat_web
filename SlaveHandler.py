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
        control_node = self.client.generateControl(control_val, idx)
        if 'params' in message:
            param_node = message['params']
            param_tree = ET.SubElement(control_node, 'params')
            param_tree.attrib['value'] = '[]' #list of params
            for param_name, param_val in message['params'].items():
                param_element = ET.SubElement(param_tree, param_name)
                param_element.attrib['value'] = param_val
        root_node.append(control_node)
        ET.dump(root_node)
        self.client.sendToEthercat(root_node)

    def receive_handler(self, node):
        reply = None
        if node.tag == self.node_name:
            for child in node:
                if child.tag == 'result':
                    for grandchild in child.getchildren():
                        if grandchild.tag == 'idx':
                            idx = int(grandchild.attrib['value'])
                            if idx in self.pending_control_from_streamer:
                                reply = self.pending_control_from_streamer[idx]
                                del self.pending_control_from_streamer[idx]
                            else:
                                pass
                    for grandchild in child.getchildren():
                        if grandchild.tag == 'return' and reply != None:
                            reply['return'] = self.eTreeToDict(grandchild)
                            string_to_send = json.dumps(reply) 
                            self.streamer.sendReply(reply)
                            pass
                elif child.tag == 'message':
                    value = child.attrib['value']
                    time = child.find('time')
                    if time != None:
                        time = time.attrib['value']
                    data = self.eTreeToDict(child.find('data'))
                    if data != None:
                        self.streamer.sendMessage(self.node_name, value, time=time, data=data)

    def eTreeToDict(self, tree):
        if tree != None:
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
        else:
            return None