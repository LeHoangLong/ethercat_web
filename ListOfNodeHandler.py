import EthercatClient
import xml.etree.ElementTree as ET

class ListOfNodehandler:
    def __init__(self, ethercat_client):
        ethercat_client.addDataHandler('list_of_nodes', self.receive_handler)
        root_node = ET.Element('list_of_nodes')
        get_list_node = ET.SubElement(root_node, 'control')
        get_list_node.attrib['value'] = 'get'
        ethercat_client.sendToEthercat(root_node)
        pass

    def receive_handler(self, node):
        ET.dump(node)

if __name__ == '__main__':
    client = EthercatClient.EthercatClient(server_name='localhost', server_port=1025)
    client.run()
    list_of_node_handler = ListOfNodehandler(client)
    pass