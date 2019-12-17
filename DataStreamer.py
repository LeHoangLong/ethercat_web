import EthercatClient
import sleekxmpp
from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.handler.callback import Callback as Callback
from sleekxmpp.xmlstream.matcher.stanzapath import StanzaPath as StanzaPath
import xml.etree.ElementTree as ET
from sleekxmpp.exceptions import *
class DataStreamer:
    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']
        self.domain_name = kwargs['domain']
        self.jid = self.name + '@' + self.domain_name
        self.password = kwargs['password']
        self.client_xmpp = None
        #self.client_xmpp.register_handler(Callback('command handler', StanzaPath('iq@type=set/set'),self.iqCommandHandler))
        self.peer_list = []
        self.online_peer = []
        self.receive_message_handler_list = []
        self.receive_command_handler_list = []
        self.connected = False
        self.is_first_connect = True

    def sendCommand(self, command):
        command_dict = {'command': command}
        self.sendMessage(command_dict)

    def iqCommandHandler(self, iq):
        print(iq['body'])
        pass

    def connect(self):
        if self.client_xmpp == None:
            self.client_xmpp = ClientXMPP(self.jid, self.password)
            self.client_xmpp.add_event_handler('session_start', self.handleConnected)
            self.client_xmpp.add_event_handler('message', self.handleIncomingMessage)
            self.client_xmpp.add_event_handler('presence_subscribe', self.handleSubscribe)
            self.client_xmpp.add_event_handler('presence_subscribed', self.handleSubscribed)
            self.client_xmpp.add_event_handler('presence_available', self.handleAvailable)
            self.client_xmpp.add_event_handler('presence_unavailable', self.handleUnavailable)
            self.client_xmpp.connect()
            self.client_xmpp.process(block=False)

    def handleConnected(self, event):
        print('handling connected')
        self.client_xmpp.send_presence()
        #self.client_xmpp.presences_received.wait(5)
        self.client_xmpp.get_roster()

        #groups = self.client_xmpp.groups()
        #for group in groups:
        #    for jid in groups[group]:
        #        sub = self.client_xmpp.client_roster[jid]['subscription']
        #        name = self.client_xmpp.client_roster[jid]['name']


        #for peer in self.client_xmpp.client_roster['hoanglong-desktop']:
        #    self.client_xmpp.send_presence(ptype='available', pto=peer)
        self.connected = True

    def handleIncomingMessage(self, message):
        for handler in self.receive_message_handler_list:
            handler(message['body'])

    def sendMessage(self, data):
        for peer in self.peer_list:
            self.client_xmpp.send_message(mto=peer, mbody=data)
            pass

    def handleAvailable(self, presence):
        from_str = str(presence['from'])
        from_str_list = from_str.split('@')
        if self.name != from_str_list[0]:
            self.peer_list.append(presence['from'])

    def handleUnavailable(self, presence):
        self.peer_list.remove(presence['from'])

    def addPeer(self, peer):
        while not self.connected:
            pass
        self.client_xmpp.send_presence_subscription(pto=peer, ptype='subscribe')

    def handleSubscribe(self, presence):
        self.client_xmpp.update_roster(presence['from'])
        self.client_xmpp.send_presence_subscription(pto=presence['from'], ptype='subscribed')

    def handleSubscribed(self, presence):
        self.client_xmpp.update_roster(presence['from'])

    def addReceiveMessageHandler(self, handler):
        self.receive_message_handler_list.append(handler)

    def addCommandHandler(self, handler):
        self.receive_command_handler_list.append(handler)

    def removeReceiveMessageHandler(self, handler):
        if handler in self.receive_message_handler_list:
            self.receive_message_handler_list.remove(handler)
            return 0
        else:
            return 1

    def stop(self):
        self.client_xmpp.disconnect(wait=True)
        self.client_xmpp = None


