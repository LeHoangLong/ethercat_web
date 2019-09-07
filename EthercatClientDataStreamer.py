from DictionaryDataStreamer import DictionaryDataStreamer
from EthercatClient import EthercatClient
import time

class EthercatClientDataStreamer(DictionaryDataStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ethercat_client = kwargs['ethercat_client']
        self.stopped = False
        self.requested_data = []

    def run(self):
        super().connect()
        self.addCommandHandler(self.dataStreamerCommandHandler)
        self.ethercat_client.addDataHandler(self.ethercatClientDataHandler)
        self.ethercat_client.run()

    def ethercatClientDataHandler(self, data):
        #print('ethercatClientDataHandler: ' + str(data))
        if type(data) is not dict:
            raise ValueError
        #print(data)
        to_send_data = {k: data[k] for k in self.requested_data}
        self.sendData(to_send_data)

    def _commandHandler(self, command):
        if command == 'stop':
            self.stop()
        elif 'add_watch' in command:
            command_split_list = command.split('_')
            self.requested_data = []
            for data_to_add in command_split_list[2:]:
                if data_to_add not in self.requested_data:
                    self.requested_data.append(data_to_add)
        elif 'motor_decelerate' in command:
            self.ethercat_client.sendToEthercat(node_name='motor', command='decelerate')
        elif 'motor_accelerate' in command:
            self.ethercat_client.sendToEthercat(node_name='motor', command='accelerate')
            


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

