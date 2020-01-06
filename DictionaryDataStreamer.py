from DataStreamer import DataStreamer
import json

class DictionaryDataStreamer(DataStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().addReceiveMessageHandler(self.receiveMessageHandler)
        self.message_handler_list = []

    def sendMessage(self, data_dict):
        data_string = json.dumps(data_dict)
        super().sendMessage(data_string)

    def addReceiveMessageHandler(self, message_handler):
        self.message_handler_list.append(message_handler)

    def receiveMessageHandler(self, message):
        data_dict = json.loads(message)
        for handler in self.message_handler_list:
            handler(data_dict)