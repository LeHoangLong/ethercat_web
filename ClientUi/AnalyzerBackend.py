from os import listdir
from os.path import isfile, join
import json
from collections import OrderedDict
from PyQt5 import QtCore

class AnalyzerBackend(QtCore.QObject):
    collected_data_updated_signal = QtCore.pyqtSignal()

    def __init__(self, path=''):
        super().__init__()
        if path == '':
            self.setStoredDataLocation('./')

    def getAvailablePlotType(self):
        return ['HISTOGRAM', 'SCATTER']

    def setStoredDataLocation(self, path):
        self.path = path
        file_list = [f for f in listdir(path) if isfile(join(path, f)) and 'collected_data_' in f] 
        collected_file = None
        self.collected_data = []
        for collected_file_name in file_list:
            try:
                collected_file = open(collected_file_name)
                if collected_file != None:
                        self.collected_data.extend(json.loads(collected_file.read(), object_pairs_hook=OrderedDict))
                        self.collected_data_updated_signal.emit()
            except Exception as e:
                print(e)
                
    def getCollectedData(self):
        return self.collected_data
