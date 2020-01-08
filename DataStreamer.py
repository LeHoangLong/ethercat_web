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
        self.presence_update_handler_list = []
        self.connected = False
        self.is_first_connect = True

    def addPresenceUpdateHandler(self, handler):
        self.presence_update_handler_list.append(handler)

    def sendCommand(self, command):
        command_dict = {'command': command}
        self.sendMessage(command_dict)

    def iqCommandHandler(self, iq):
        print(iq['body'])
        for handler in self.receive_command_handler_list:
            handler(iq)

    def connect(self, block=True):
        if self.client_xmpp == None:
            self.client_xmpp = ClientXMPP(self.jid, self.password)
            self.client_xmpp.add_event_handler('session_start', self.handleConnected)
            self.client_xmpp.add_event_handler('message', self.handleIncomingMessage)
            self.client_xmpp.add_event_handler('presence_subscribe', self.handleSubscribe)
            self.client_xmpp.add_event_handler('presence_subscribed', self.handleSubscribed)
            self.client_xmpp.add_event_handler('presence_available', self.handleAvailable)
            self.client_xmpp.add_event_handler('presence_unavailable', self.handleUnavailable)
            self.client_xmpp.add_event_handler('presence_probe', self.handle_probe)
            self.client_xmpp.connect()
            self.client_xmpp.process()
            while self.connected == False:
                pass


    def handle_probe(self, presence):
        sender = presence['from']
        self.send_presence(pto=sender)

    def probe_presence(self):
        for peer in self.peer_list:
            self.client_xmpp.send_presence(pto=peer['jid'], ptype='probe')
            
    def handleConnected(self, event):
        self.client_xmpp.send_presence()
        while len(self.client_xmpp.client_roster) == 0:
            self.client_xmpp.get_roster()

        for roster in self.client_xmpp.client_roster:
            contact = {
                'jid': roster,
                'status': 'UNAVAILABLE'
            }
            self.peer_list.append(contact)

        self.probe_presence()

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
            if peer['status'] == 'AVAILABLE':
                self.client_xmpp.send_message(mto=peer['jid'], mbody=data)
            pass
        
    def getListOfPeers(self):
        return self.peer_list
        
    def handleAvailable(self, presence):
        for peer in self.peer_list:
            if peer['jid'] == presence['from'].bare:
                print('peer available: ' + peer['jid'])
                peer['status'] = 'AVAILABLE'
        
        for handler in self.presence_update_handler_list:
            handler(peer)

    def handleUnavailable(self, presence):
        for peer in self.peer_list:
            if peer['jid'] == presence['from'].bare:
                peer['status'] = 'UNAVAILABLE'

        for handler in self.presence_update_handler_list:
            handler(peer)


    def addPeer(self, peer):
        while not self.connected:
            pass
        self.client_xmpp.send_presence_subscription(pto=peer, ptype='subscribe')

    def handleSubscribe(self, presence):
        self.client_xmpp.update_roster(presence['from'])
        self.client_xmpp.send_presence_subscription(pto=presence['from'], ptype='subscribed')
        contact = {
            'jid': presence['from'].bare,
            'status': 'UNAVAILABLE'
        }
        self.peer_list.append(contact)
        self.probe_presence()

    def handleSubscribed(self, presence):
        self.client_xmpp.update_roster(presence['from'])
        contact = {
            'jid': roster,
            'status': 'UNAVAILABLE'
        }
        self.peer_list.append(contact)
        self.probe_presence()

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


