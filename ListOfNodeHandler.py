import EthercatClient
import xml.etree.ElementTree as ET
import EthercatSlaveHandler
import EthercatClientDataStreamer
import DictionaryDataStreamer
import SlaveHandler

class ListOfNodehandler:
    def __init__(self, ethercat_client, streamer):
        self.node_name = 'list_of_nodes'
        ethercat_client.addDataHandler(self.node_name, self.receive_handler)
        root_node = ET.Element(self.node_name)

        control_node = ethercat_client.generateControl('get')

        root_node.append(control_node)
        ethercat_client.sendToEthercat(root_node)
        self.ethercat_client = ethercat_client
        self.streamer = streamer
        self.streamer.addReceiveMessageHandler(self.streamer_rx_message_handler)
        self.slave_node_list = []

    def streamer_rx_message_handler(self, message_dict):
        for node_msg_key in message_dict:
            if node_msg_key == 'list_of_nodes':
                json_dict = {}
                node_message_list = message_dict[node_msg_key]
                for message in node_message_list:
                    if message.key()[0] == 'control':
                        control_list = message_dict[message_key]
                        for control in control_list:
                            if (type(control) == str):
                                if control == 'get':
                                    json_dict = {self.node_name: self.slave_node_list}
                        
                self.streamer.sendMessage(json_dict)    


    def receive_handler(self, node):
        ET.dump(node)
        for child in node:
            if child.tag == 'result':
                if 'value' in child.attrib and child.attrib['value'] == 'get':
                    if child.find('status').attrib['value'] == 'ok':
                        for node in child:
                            if node.tag != 'idx' and node.tag != 'status':
                                slave = SlaveHandler.SlaveHandler(self.ethercat_client, node.tag, self.streamer)
                                self.slave_node_list.append(slave)
        pass
        #ethercat_slave = EthercatSlaveHandler.EthercatSlaveHandler(self.ethercat_client, 'test_node')
        #ethercat_streamer = EthercatClientDataStreamer.EthercatClientDataStreamer(ethercat_slave, self.streamer)
        #self.slave_node_list.append(ethercat_streamer)

if __name__ == '__main__':
    client = EthercatClient.EthercatClient(server_name='localhost', server_port=1025)
    client.run()
    streamer = DictionaryDataStreamer.DictionaryDataStreamer(name='long', domain='hoanglong',\
         password='123')
    list_of_node_handler = ListOfNodehandler(client, streamer)