import time
import EthercatSlaveHandler

class EthercatClientDataStreamer():
    def __init__(self, slave_handler, streamer):
        self.slave_handler = slave_handler
        self.streamer = streamer
        self.stopped = False
        self.requested_data = []
        self.slave_handler.addMessageHandler(self.ethercatClientMessageHandler)
        self.streamer.addCommandHandler(self.dataStreamerCommandHandler)
        self.streamer.addReceiveMessageHandler(self.streamerMessageHandler)
        
    def run(self):
        self.streamer.connect()

    def ethercatClientMessageHandler(self, data):
        for packet in data:
            self.streamer.sendMessage(packet)

    def streamerMessageHandler(self, data):
        self.slave_handler.sendMessage(data)
            

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
            self.slave_handler.sendControl(node_name='motor', command='decelerate')
        elif 'motor_accelerate' in command:
            self.slave_handler.sendControl(node_name='motor', command='accelerate')
            


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
        self.stopped = True

