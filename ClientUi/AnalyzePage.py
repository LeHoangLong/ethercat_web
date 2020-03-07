from PyQt5 import QtWidgets, QtCore, QtGui
from SelectPath import SelectPath
from os import listdir
from os.path import isfile, join
import json
from collections import OrderedDict
from CollectedSpreadsheet import CollectedSpreadsheet
from PlotPage import PlotPage
from AnalyzerBackend import AnalyzerBackend

class AnalyzePage(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend = AnalyzerBackend()
        self.spreadsheet = CollectedSpreadsheet(self)
        self.addTab(self.spreadsheet, "Sheet")
        self.add_tab_widget = QtWidgets.QWidget(self)
        self.addTab(self.add_tab_widget, QtGui.QIcon.fromTheme('list-add'), '') 
        self.tab_count = 2
        self.tabBarClicked.connect(self.tabClickedHandler)
        #self.setTabsClosable(True)
        #self.tabCloseRequested.connect(self.tabCloseHandler)

    def tabClickedHandler(self, idx):
        if idx == self.tab_count - 1:
            new_widget = PlotPage(self.backend, self)
            close_button = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('window-close'), '')
            close_button.setFlat(True)
            close_button.clicked.connect(lambda: self.tabCloseHandler(idx))
            self.insertTab(idx, new_widget, 'new_tab')
            self.tabBar().setTabButton(idx, QtWidgets.QTabBar.RightSide, close_button)
            self.tab_count += 1

    def tabCloseHandler(self, idx):
        self.removeTab(idx)
        self.tab_count -= 1

