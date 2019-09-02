from DictionaryDataStreamer import DictionaryDataStreamer
from EthercatClient import EthercatClient
import time

class EthercatClientDataStreamer(DictionaryDataStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ethercat_client = kwargs['ethercat_client']
        self.stopped = False

    def run(self):
        super().run()
        self.addCommandHandler(self.dataStreamerCommandHandler)
        self.ethercat_client.addDataHandler(self.ethercatClientDataHandler)
        self.ethercat_client.run()

    def ethercatClientDataHandler(self, data):
        #print('ethercatClientDataHandler: ' + str(data))
        if type(data) is not dict:
            raise ValueError
        self.sendData(data)

    def _commandHandler(self, command):
        if command == 'stop':
            self.stop()

    def waitTillStopped(self):
        while self.stopped == False:
            pass

    def dataStreamerCommandHandler(self, command_list_str):
        command_list = command_list_str.split(':')
        for i in range(len(command_list)):
            if command_list[i] == 'command':
                command = command_list[i + 1]
                self._commandHandler(command)

        pass

    def stop(self):
        self.ethercat_client.disconnect()
        super().stop()
        self.stopped = True

