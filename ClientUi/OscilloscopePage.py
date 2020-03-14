from PyQt5 import QtWidgets, QtCore, QtGui
from NodeTree import NodeTree
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
from DualButtonWidget import DualButtonWidget
from functools import partial
import numpy as np
from threading import Thread, Lock
import time
import pyqtgraph as pg

class ChannelSelect(QtWidgets.QWidget):
    def __init__(self, channel_number, parent=None):
        super().__init__(parent)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.check_box = QtWidgets.QCheckBox()
        self.main_layout.addWidget(self.check_box)
        self.check_box.setChecked(False)
        self.check_box.stateChanged.connect(self.checkBoxStateChangeHandler)
        self.is_enabled = self.check_box.checkState()
        self.data_name = ''

        self.channel_number = channel_number

        self.button = QtWidgets.QPushButton("Channel " + str(channel_number))
        self.text = QtWidgets.QLabel("")
        self.text.setStyleSheet("background-color: grey; border-width: 1px; border-style: solid; border-color: black;")

        self.main_layout.addWidget(self.button, stretch=1)
        self.main_layout.addWidget(self.text, stretch=20)

    def checkBoxStateChangeHandler(self, is_checked):
        self.is_enabled = is_checked
        if self.is_enabled:
            self.text.setText(self.data_name)
            self.text.setStyleSheet('background-color: white; border-width: 1px; border-style: solid; border-color: black;')
        else:
            self.text.setText('')
            self.text.setStyleSheet('background-color: grey; border-width: 1px; border-style: solid; border-color: black;')
    
    def setDataName(self, data_name):
        self.data_name = data_name
        self.check_box.setChecked(True)
        self.text.setText(data_name)
        
    def isEnabled(self):
        is_enabled = self.is_enabled and self.text.text() != ''
        return is_enabled

class SelectChannelDialog(QtWidgets.QDialog):
    channel_selected_signal = QtCore.pyqtSignal(str, str)
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.main_layout = QtWidgets.QHBoxLayout()
        self.node_tree = NodeTree(self.backend, self)
        self.node_tree.setItemFlag(QtCore.Qt.ItemIsUserCheckable)
        self.node_tree.showAllNodeData()
        self.main_layout.addWidget(self.node_tree)
        self.button = DualButtonWidget("Ok", "Cancel", direction=1)
        self.main_layout.addWidget(self.button)
        self.button.button_2.clicked.connect(self.cancelClickHandler)
        self.button.button_1.clicked.connect(self.okClickHandler)
        self.setLayout(self.main_layout)

    def cancelClickHandler(self):
        self.close()

    def okClickHandler(self):
        selected_data_name = self.node_tree.getSelectedDataName()
        selected_data_type = self.node_tree.getSelectedDataType()
        if selected_data_name != None:
            self.channel_selected_signal.emit(selected_data_name, selected_data_type)
        self.close()


class OscilloscopePage(QtWidgets.QWidget):
    updateGraphSignal = QtCore.pyqtSignal(int)
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.data_lock = Lock()
        self.updateGraphSignal.connect(self.updateSignalHandler)

        self.start_stop_button = DualButtonWidget("Start", "Stop")
        self.start_stop_button.button_1.clicked.connect(self.playButtonClickHandler)
        self.start_stop_button.button_2.clicked.connect(self.stopButtonClickHandler)
        self.main_layout.addWidget(self.start_stop_button)
        
        self.plotWidget = pg.PlotWidget(parent=self)
        self.main_layout.addWidget(self.plotWidget)

        self.num_of_channel = 4
        color_list = ['r', 'g', 'b','y']
        self.channel_list = []
        for i in range(self.num_of_channel):
            channel = ChannelSelect(i)
            channel_dict = {
                't': [],
                'y': [],
                'channel_select_widget': channel,
                'data_name': '',
                'data_type': 'int',
                'data_watcher': partial(self.dataWatchHandler, channel_number=i),
                'color': color_list[i],
                'counter': 0
            }

            self.channel_list.append(channel_dict)
            #line = Line2D(channel_dict['t'], channel_dict['y'])
            #line.set_animated(True)
            #self.ax.add_line(line)
            line = self.plotWidget.plot(connect='all', pen=channel_dict['color'])
            channel_dict['line'] = line
            self.main_layout.addWidget(channel)
            channel.button.clicked.connect(partial(self.channelButtonClickeHandler, i))

    def channelButtonClickeHandler(self, channel_number):
        self.channel_select_dialog = SelectChannelDialog(self.backend)
        self.channel_select_dialog.channel_selected_signal.connect(partial(self.channelUpdateHandler, channel_number=channel_number))
        self.channel_select_dialog.show()
        self.channel_select_dialog.setModal(True)
        pass

    def channelUpdateHandler(self, data_name, data_type, channel_number):
        self.channel_list[channel_number]['channel_select_widget'].setDataName(data_name)
        self.channel_list[channel_number]['data_name'] = data_name
        self.channel_list[channel_number]['data_type'] = data_type

    def playButtonClickHandler(self):

        for channel_number, channel in enumerate(self.channel_list):
            channel_select_widget = channel['channel_select_widget']
            self.backend.removeDataWatch(self.channel_list[channel_number]['data_watcher'])
            if channel_select_widget.isEnabled():
                self.backend.addDataWatch(self.channel_list[channel_number]['data_watcher'], channel['data_name'], channel['data_type'])

        self.backend.enableDataCollection()

    def stopButtonClickHandler(self):
        self.backend.disableDataCollection()

    def dataWatchHandler(self, data, time, data_type, channel_number):
        #self.data_lock.acquire()
        channel = self.channel_list[channel_number]
        if len(channel['t']) > 150:
            del channel['t'][0]
            del channel['y'][0]

        if data_type == 'int' or data_type == 'float':
            channel['t'].append(time)
            channel['y'].append(data)
            channel['counter'] += 1

        if channel['counter'] > 20:
            channel['counter'] = 0
            self.updateGraphSignal.emit(channel_number)
        #self.data_lock.release()
        #if line in self.ax.lines:
        #    self.ax.lines.remove(line)
        #channel['line'], = self.ax.plot(channel['t'], channel['y'], channel['color'])
        #line = self.ax.add_line(line)
        #channel['line'] = self.ax.add_line(line)
        #self.ax.relim()
        #self.ax.autoscale_view()
        #self.ax.plot(channel['t'], channel['y'], channel['color'])
        #plt.draw()
        #self.plot.canvas.draw()

    def updateSignalHandler(self, channel_number):
        #self.data_lock.acquire()
        channel = self.channel_list[channel_number]
        line = channel['line']
        line.setData(channel['t'], channel['y'])
        self.plotWidget.repaint()
        #self.data_lock.release()



    
        