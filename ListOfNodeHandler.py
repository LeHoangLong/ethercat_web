import EthercatClient
import xml.etree.ElementTree as ET
import EthercatSlaveHandler

class ListOfNodehandler:
    def __init__(self, ethercat_client):
        ethercat_client.addDataHandler('list_of_nodes', self.receive_handler)
        root_node = ET.Element('list_of_nodes')

        control_node = ethercat_client.generateControl('get')

        root_node.append(control_node)
        ethercat_client.sendToEthercat(root_node)
        self.ethercat_client = ethercat_client

    def receive_handler(self, node):
        ET.dump(node)
        self.slave = EthercatSlaveHandler.EthercatSlaveHandler(self.ethercat_client, 'test_node')

if __name__ == '__main__':
    client = EthercatClient.EthercatClient(server_name='localhost', server_port=1025)
    client.run()
    list_of_node_handler = ListOfNodehandler(client)
    while True:
        pass