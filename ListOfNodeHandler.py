import EthercatClient
import xml.etree.ElementTree as ET
import EthercatSlaveHandler
import EthercatClientDataStreamer
import DictionaryDataStreamer
import SlaveHandler

class ListOfNodehandler:
    def __init__(self, ethercat_client, streamer):
        self.node_name = 'list_of_nodes'
        self.ethercat_client = ethercat_client
        self.streamer = streamer
        self.slave_node_list = []
        self.slave_name_list = []

        root_node = ET.Element(self.node_name)
        control_node = ethercat_client.generateControl('get')
        root_node.append(control_node)
        self.ethercat_client.sendToEthercat(root_node)

        self.ethercat_client.addDataHandler(self.node_name, self.receive_handler)
        self.streamer.addReceiveMessageHandler(self.streamer_rx_message_handler)
        self.streamer.addReceiveControlHandler(self.node_name, self.streamerRxControlHandler)

    def streamerRxControlHandler(self, message, reply):
        value = message['value']
        if value == 'get':
            reply['return'] = {'nodes': self.slave_name_list}
        return True
        

    def streamer_rx_message_handler(self, message_list):
        pass


    def receive_handler(self, node):
        ET.dump(node)
        for child in node:
            if child.tag == 'result':
                if 'value' in child.attrib and child.attrib['value'] == 'get':
                    if child.find('status').attrib['value'] == 'ok':
                        for node in child:
                            if node.tag == 'return':
                                for node_name in node:
                                    slave = SlaveHandler.SlaveHandler(self.ethercat_client, node_name.tag, self.streamer)
                                    self.slave_node_list.append(slave)
                                    self.slave_name_list.append(node_name.tag)
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