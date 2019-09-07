from DataStreamer import DataStreamer

class DictionaryDataStreamer(DataStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().addReceiveMessageHandler(self.receiveDataHandler)
        self.handler_list = []

    def sendData(self, data):
        data_string = ''
        for key, val in data.items():
            data_string += key + ':' + val + ';'
        print(data_string)
        super().sendData(data_string)

    def addReceiveMessageHandler(self, handler):
        self.handler_list.append(handler)

    def receiveDataHandler(self, message):
        data_dict = {}
        message_list = message.split(';')
        for data in message_list:
            data_list = data.split(':')
            data_dict[data_list[0]] = data_list[1]
        print(data_dict)
        for handler in self.handler_list:
            handler(data_dict)