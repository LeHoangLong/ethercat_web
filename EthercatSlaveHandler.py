import EthercatClient
import xml.etree.ElementTree as ET

class EthercatSlaveHandler:
    def __init__(self, ethercat_client, node_name):
        print('ethercat slave created')
        ethercat_client.addDataHandler(node_name, self.receive_handler)

    def receive_handler(self, node):
        ET.dump(node)
