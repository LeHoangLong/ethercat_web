import EthercatClient
import xml.etree.ElementTree as ET
import EthercatSlaveHandler
import EthercatClientDataStreamer
import DictionaryDataStreamer

class ListOfNodehandler:
    def __init__(self, ethercat_client, streamer):
        ethercat_client.addDataHandler('list_of_nodes', self.receive_handler)
        root_node = ET.Element('list_of_nodes')

        control_node = ethercat_client.generateControl('get')

        root_node.append(control_node)
        ethercat_client.sendToEthercat(root_node)
        self.ethercat_client = ethercat_client
        self.streamer = streamer
        self.slave_node_list = []

    def receive_handler(self, node):
        ethercat_slave = EthercatSlaveHandler.EthercatSlaveHandler(self.ethercat_client, 'test_node')
        ethercat_streamer = EthercatClientDataStreamer.EthercatClientDataStreamer(ethercat_slave, self.streamer)
        self.slave_node_list.append(ethercat_streamer)

if __name__ == '__main__':
    client = EthercatClient.EthercatClient(server_name='localhost', server_port=1025)
    client.run()
    streamer = DictionaryDataStreamer.DictionaryDataStreamer(name='long', domain='hoanglong',\
         password='123')
    list_of_node_handler = ListOfNodehandler(client, streamer)