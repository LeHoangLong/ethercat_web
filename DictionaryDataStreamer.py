from DataStreamer import DataStreamer
import json
import threading
import time

class DictionaryDataStreamer(DataStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().addReceiveMessageHandler(self.receiveMessageHandler)
        self.message_handler_list = []
        self.message_counter = 0
        self.pending_message_list = []
        self.sent_message_received = False
        self.sem = threading.Semaphore(0)
        #self.update_thread = threading.Thread(target=self.flushThread).start()
        self.waiting_type = None
        self.waiting_idx = 0
        self.waiting_node = None
        self.reply_handler_dict = {}
        self.control_handler_dict = {}

    #def flushThread(self):
    #    time.sleep(0.1)
    #    self.flushOut()
        
    def sendControl(self, node_name, value, param=None, reply_handler=None):
        new_message = {
            'node': node_name,
            'idx': self.message_counter,
            'type': 'control',
            'value': value
        }

        if param != None:
            new_message['param'] = param

        self.pending_message_list.append(new_message)
        if reply_handler != None:
            self.reply_handler_dict[self.message_counter] = reply_handler
        self.flushOut()
        self.message_counter += 1

    def sendReply(self, reply):
        self.pending_message_list.append(reply)
        self.flushOut()
        pass

    def flushOut(self):
        if len(self.pending_message_list) > 0:
            data_string = json.dumps(self.pending_message_list)
            super().sendMessage(data_string)

    def addReceiveMessageHandler(self, message_handler):
        self.message_handler_list.append(message_handler)

    def addReceiveControlHandler(self, node_name, control_handler):
        self.control_handler_dict[node_name] = control_handler

    def receiveMessageHandler(self, message):
        message_list = json.loads(message)
        for message in message_list:
            if 'type' in message:
                if message['type'] == 'reply':
                    if 'idx' in message and message['idx'] in self.reply_handler_dict:
                        self.reply_handler_dict[message['idx']](message)
                        self.reply_handler_dict.pop(message['idx'])
                elif message['type'] == 'control':
                    if 'node' in message and message['node'] in self.control_handler_dict:
                        reply = {
                            'node': message['node'],
                            'idx': message['idx'],
                            'type': 'reply',
                            'value': ''
                        }
                        immediate_reply = self.control_handler_dict[message['node']](message, reply)
                        if immediate_reply != True:
                            self.sendReply(reply)
                elif message['type'] == 'message':
                    for handler in self.message_handler_list:
                        handler(message)
                    