from DictionaryDataStreamer import DictionaryDataStreamer
from EthercatClientDataStreamer import EthercatClientDataStreamer
from EthercatClient import EthercatClient
import threading
from SimulatedEthercatMasterServer import SimulatedEthercatMasterServer
import time
from multiprocessing import Process

def receiveMessageHandler(message):
    print('from: ' + str(message['from']))
    print('to: ' + str(message['to']))
    print('received message 2: ' + str(message['body']))
    print('received time2 : ' + str(time.time() * 1000))

def create_streamer_1():
    my_name = 'le.hoang.long@xmpp.jp'
    peer_name = 'le.hoang.long.2@xmpp'
    my_password = 'xmpp.jp'
    #domain_name = '35.189.58.5'
    my_name = 'long'
    peer_name = 'long_2@hoanglong'
    my_password = '123'
    client = EthercatClient(server_name='localhost', server_port=1025)
    streamer = EthercatClientDataStreamer(name=my_name, domain='hoanglong-desktop',\
         password=my_password, ethercat_client=client)
    streamer.run()
    print('streamer 1 run')
    streamer.waitTillStopped()
    print('streamer 1 done')

def create_streamer_2():
    my_name = 'le.hoang.long.2@xmpp.jp'
    peer_name = 'le.hoang.long@xmpp'
    my_password = 'xmpp.jp'
    #domain_name = '35.189.58.5'
    #domain_name = 'hoanglong-desktop'
    my_name = 'long_2'
    peer_name = 'long@hoanglong'
    my_password = '123'

    #streamer_2 = DictionaryDataStreamer(jid=my_name, password=my_password)
    streamer_2 = DictionaryDataStreamer(name=my_name, domain='hoanglong-desktop',\
         password=my_password)
    streamer_2.addReceiveMessageHandler(receiveMessageHandler)
    streamer_2.connect()
    time.sleep(5)
    print('streamer 2 run')
    streamer_2.sendCommand('add_watch_sensor1')
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