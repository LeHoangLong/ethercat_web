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
        collected_file_0 = None
        for collected_file in file_list:
            collected_file_0 = open(collected_file)
        if collected_file_0 != None:
            self.collected_data = json.loads(collected_file_0.read(), object_pairs_hook=OrderedDict)
            self.collected_data_updated_signal.emit()

    def getCollectedData(self):
        return self.collected_data
