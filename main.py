from DictionaryDataStreamer import DictionaryDataStreamer
from EthercatClient import EthercatClient
import threading
from SimulatedEthercatMasterServer import SimulatedEthercatMasterServer
import time
from multiprocessing import Process
from ListOfNodeHandler import ListOfNodehandler

def receiveMessageHandler(message):
    print('main handler')
    print(message)
    print('from: ' + str(message['from']))
    print('to: ' + str(message['to']))
    print('received message 2: ' + str(message['body']))
    print('received time2 : ' + str(time.time() * 1000))

def reply_handler(reply):
    print(reply)
    pass

def message_handler(message):
    print(message)
    pass

def create_streamer_1():
    my_name = 'le.hoang.long@xmpp.jp'
    peer_name = 'le.hoang.long.2@xmpp'
    my_password = 'xmpp.jp'
    #domain_name = '35.189.58.5'
    my_name = 'long'
    peer_name = 'long_2@35.244.75.175'
    my_password = '123'
    client = EthercatClient(server_name='localhost', server_port=1025)
    client.run()
    #streamer = DictionaryDataStreamer(name='long', domain='long-inspiron-5447',\
    #     password='123')
    # 
    streamer = DictionaryDataStreamer(name='long', domain='34.87.175.118',\
        password='123')

    #peer_name = 'long_2@long-inspiron-5447'
    peer_name = 'long_2@34.87.175.118'

    streamer.connect()

    peer_name = 'long_2@hoanglong-desktop'
    #peer_name = 'long@xmpp'
    #streamer.addPeer(peer_name)

    list_of_node_handler = ListOfNodehandler(client, streamer)
    

    #streamer.addPeer(peer_name)
    while True:
        pass

    
def streamer_2_reply_handler(message):
    print(message)
    pass

def create_streamer_2():
    my_name = 'le.hoang.long.2@xmpp.jp'
    peer_name = 'le.hoang.long@xmpp'
    my_password = 'xmpp.jp'
    #domain_name = '35.189.58.5'
    #domain_name = 'long-inspiron-5447'
    my_name = 'long_2'
    peer_name = 'long@35.244.75.175'
    my_password = '123'
    #peer_name = 'long_2@long-inspiron-5447'
    peer_name = 'long_2@34.87.175.118'

    #streamer_2 = DictionaryDataStreamer(jid=my_name, password=my_password)
    #streamer_2 = DictionaryDataStreamer(name='le.hoang.long.2', domain='xmpp.jp',\
    #     password='xmpp.jp')
    #streamer_2 = DictionaryDataStreamer(name='long_2', domain='long-inspiron-5447',\
    #     password='123')
    streamer_2 = DictionaryDataStreamer(name='long_2', domain='34.87.175.118',\
        password='123')

    #streamer_2.addReceiveMessageHandler(receiveMessageHandler)
    streamer_2.connect()
    peer_name = 'long@hoanglong-desktop'
    peer_name = 'long@34.87.175.118'
    #peer_name = 'long@xmpp'
    streamer_2.addPeer(peer_name)
    #time.sleep(5)
    #streamer_2.sendControl('test_node', 'type', reply_handler=reply_handler)
    #streamer_2.addReceiveMessageHandler(message_handler)

    #param = {
    #    "run": "1"
    #}

    while True:
        #streamer_2.sendControl('program', 'get_states', param=param, reply_handler=streamer_2_reply_handler)
        #test_request = [{'list_of_nodes': {'control': 'get'}}, {'test_node_2' : [{'control': 'type'}]}]
        #test_request = [
        #    {'node': 'list_of_nodes', 'type': 'control', 'value': 'get'}
            #{'node': 'test_node_2', 'type': 'control', 'value': 'type'}
        #]
        #streamer_2.sendControl('list_of_nodes', 'get', reply_handler=reply_handler)
        time.sleep(5)
    print('streamer 2 run')
    time.sleep(100)
    streamer_2.stop()
    
if __name__ == "__main__":
    p = threading.Thread(target=create_streamer_1)
    #p_2 = threading.Thread(target=create_streamer_2)
    p.start()
    #p_2.start()
    p.join()
    #p_2.join()
    print('done')
    pass