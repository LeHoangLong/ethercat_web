from PyQt5 import QtWidgets, QtCore
from SelectPath import SelectPath
from os import listdir
from os.path import isfile, join
import json
from collections import OrderedDict

class CollectedSpreadsheet(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.select_path = SelectPath('Select saved location')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.spreadsheet = QtWidgets.QTableWidget()
        self.main_layout.addWidget(self.select_path)
        self.main_layout.addWidget(self.spreadsheet)
        
        self.select_path.selected_path_changed_signal.connect(self.selectedPathChangedHandler)
        self.table_item_list = []

    def selectedPathChangedHandler(self):
        self.table_item_list = []
        path = self.select_path.getSelectedPath()
        collected_data = self.backend.getCollectedData(path)
        row_number = 0
        self.spreadsheet.setRowCount(len(collected_data))
        self.spreadsheet.setColumnCount(len(collected_data[0]))
        self.spreadsheet.setHorizontalHeaderLabels(collected_data[0].keys())
        for sample in collected_data:
            col_number = 0
            for data_name, data in sample.items():
                item_widget = QtWidgets.QTableWidgetItem(str(data))
                self.table_item_list.append(item_widget)
                self.spreadsheet.setItem(row_number, col_number, item_widget)
                col_number += 1
            row_number += 1

