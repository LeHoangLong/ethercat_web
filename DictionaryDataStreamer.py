from DataStreamer import DataStreamer

class DictionaryDataStreamer(DataStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sendData(self, data):
        data_string = ''
        for key, val in data.items():
            data_string += key + ':' + val
        print(data_string)
        super().sendData(data_string)

    