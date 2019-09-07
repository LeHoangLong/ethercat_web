# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
import DictionaryDataStreamer as Streamer
from PyQt5.QtCore import *
import time
import pyqtgraph.pyqtgraph as pg
import numpy as np

class Worker(QThread):
    data_receive_signal = pyqtSignal(dict)
    def __init__(self, streamer):
        super(Worker, self).__init__()
        self.streamer = streamer
        self.streamer.addReceiveMessageHandler(self.receive_message_handler)

    @pyqtSlot(str)
    def connect_button_clicked(self, click_type):
        if click_type == 'connect':
            self.streamer.connect()
        else:
            self.streamer.stop()

    @pyqtSlot(tuple)
    def refresh_watch_list(self, data_names):
        command_to_send = 'add_watch'
        i = 0
        for name in data_names:
            command_to_send += '_' + name
            i += 1
        self.streamer.sendCommand(command_to_send)

    @pyqtSlot(str)
    def remove_watch_button_clicked(self, data_name):
        command_to_send = 'remove_watch_' + data_name
        self.streamer.sendCommand(command_to_send)

    def receive_message_handler(self, data):
        self.data_receive_signal.emit(data)

class Ui_Dialog(QObject):
    connect_or_disconnect_signal = pyqtSignal(str)
    refresh_watch_list_signal = pyqtSignal(tuple)
    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog):
        self.streamer = Streamer.DictionaryDataStreamer(name='long_2', domain='hoanglong-desktop',\
             password='123')

        self.worker = Worker(self.streamer)
        self.thread_obj = QThread()
        self.worker.moveToThread(self.thread_obj)
        self.thread_obj.start()
        self.curve_dict = {}
        
        Dialog.setObjectName("Dialog")
        Dialog.resize(508, 400)
        self.data_view_frame = QtWidgets.QFrame(Dialog)
        self.data_view_frame.setGeometry(QtCore.QRect(10, 10, 321, 381))
        self.data_view_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.data_view_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.data_view_frame.setObjectName("data_view_frame")
        self.connect_button = QtWidgets.QPushButton(Dialog)
        self.connect_button.setGeometry(QtCore.QRect(350, 10, 151, 21))
        self.connect_button.setObjectName("connect_button")
        self.connect_button.clicked.connect(self.connect_button_clicked)
        self.select_data_frame = QtWidgets.QFrame(Dialog)
        self.select_data_frame.setGeometry(QtCore.QRect(340, 40, 171, 151))
        self.select_data_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.select_data_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.select_data_frame.setObjectName("select_data_frame")
        self.add_data_type_watch = QtWidgets.QPushButton(self.select_data_frame)
        self.add_data_type_watch.setGeometry(QtCore.QRect(10, 120, 71, 25))
        self.add_data_type_watch.setObjectName("add_data_type_watch")
        self.add_data_type_watch.clicked.connect(self.add_data_watch_clicked)
        self.remove_data_type_watch = QtWidgets.QPushButton(self.select_data_frame)
        self.remove_data_type_watch.setGeometry(QtCore.QRect(90, 120, 71, 25))
        self.remove_data_type_watch.setObjectName("remove_data_type_watch")
        self.available_data_type_list = QtWidgets.QListWidget(self.select_data_frame)
        self.available_data_type_list.setGeometry(QtCore.QRect(10, 10, 151, 101))
        self.available_data_type_list.setObjectName("available_data_type_list")
        self.available_data_type_list.addItem('sensor1')
        self.available_data_type_list.addItem('sensor2')
        self.available_data_type_list.addItem('time')
        self.item_activated = {'sensor1': False, 'sensor2': False, 'time': False}
        self.available_data_type_list.itemActivated.connect(self.data_list_activated)
        self.command_frame = QtWidgets.QFrame(Dialog)
        self.command_frame.setGeometry(QtCore.QRect(340, 220, 171, 171))
        self.command_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.command_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.command_frame.setObjectName("command_frame")
        self.command_list = QtWidgets.QListView(self.command_frame)
        self.command_list.setGeometry(QtCore.QRect(10, 10, 151, 121))
        self.command_list.setObjectName("command_list")
        self.command_send_button = QtWidgets.QPushButton(self.command_frame)
        self.command_send_button.setGeometry(QtCore.QRect(10, 140, 151, 25))
        self.command_send_button.setObjectName("command_send_button")

        self.connect_or_disconnect_signal.connect(self.worker.connect_button_clicked)
        self.refresh_watch_list_signal.connect(self.worker.refresh_watch_list)

        self.disconnect = True
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        data = np.random.randn(5000)
        self.plot_widget_1 = pg.PlotWidget()
        self.plot_widget_1.enableAutoRange()
        self.plot_widget_2 = pg.PlotWidget()
        self.plot_widget_2.enableAutoRange()
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.plot_widget_1)
        self.layout.addWidget(self.plot_widget_2)
        self.data_view_frame.setLayout(self.layout)
        self.setPlotCurve('sensor1', self.plot_widget_1.plot())
        self.setPlotCurve('sensor2', self.plot_widget_2.plot())
        self.worker.data_receive_signal.connect(self.data_received_handler)
        
    def setPlotCurve(self, curve_name, curve):
        self.curve_dict[curve_name] = {}
        self.curve_dict[curve_name]['curve'] = curve
        self.curve_dict[curve_name]['data'] = np.zeros(100)

    def retranslateUi(self, Dialog):
        self._translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(self._translate("Dialog", "Dialog"))
        self.connect_button.setText(self._translate("Dialog", "Connect"))
        self.add_data_type_watch.setText(self._translate("Dialog", "Add"))
        self.remove_data_type_watch.setText(self._translate("Dialog", "Remove"))
        self.command_send_button.setText(self._translate("Dialog", "Send"))

    def connect_button_clicked(self):
        if self.disconnect == True:
            self.connect_or_disconnect_signal.emit('connect')
            self.connect_button.setText(self._translate("Dialog", "Disconnect"))
            self.disconnect = False
        else:
            self.connect_or_disconnect_signal.emit('disconnect')
            self.connect_button.setText(self._translate("Dialog", "Connect"))
            self.disconnect = True

    def data_list_activated(self, item):
        self.item_activated[item.text()] = not self.item_activated[item.text()]
        font = QFont()
        if self.item_activated[item.text()] == True:
            font.setBold(True)
        else:
            font.setBold(False)
        item.setFont(font)

    def add_data_watch_clicked(self):
        self.requested_items = []
        for k, v in self.item_activated.items():
            if v == True:
                self.requested_items.append(k)
        watch_tuple = tuple(self.requested_items)
        self.refresh_watch_list_signal.emit(watch_tuple)
        pass

    @pyqtSlot(dict)
    def data_received_handler(self, data):
        for data_name, data_val in data.items():
            if data_name != 'time':
                self.curve_dict[data_name]['data'] = np.roll(self.curve_dict[data_name]['data'], -1)
                print(data_val)
                self.curve_dict[data_name]['data'][-1] = data_val
                self.curve_dict[data_name]['curve'].setData(self.curve_dict[data_name]['data'])
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

