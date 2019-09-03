# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import DictionaryDataStreamer as Streamer
from PyQt5.QtCore import QThreadPool, QRunnable, QThread, pyqtSignal, pyqtSlot, QObject
import time

class Worker(QThread):
    def __init__(self, streamer):
        super(Worker, self).__init__()
        self.streamer = streamer
        self.streamer.addReceiveMessageHandler(self.receive_message_handler)

    @pyqtSlot(str)
    def connect_button_clicked(self, type):
        if type == 'connect':
            self.streamer.connect()
        else:
            self.streamer.stop()

    def receive_message_handler(self, message):
        print(message)

class Ui_Dialog(QObject):
    connect_or_disconnect_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog):
        self.streamer = Streamer.DictionaryDataStreamer(name='long_2', domain='hoanglong-desktop',\
             password='123')

        self.worker = Worker(self.streamer)
        self.thread_obj = QThread()
        self.worker.moveToThread(self.thread_obj)
        self.thread_obj.start()
        
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
        self.remove_data_type_watch = QtWidgets.QPushButton(self.select_data_frame)
        self.remove_data_type_watch.setGeometry(QtCore.QRect(90, 120, 71, 25))
        self.remove_data_type_watch.setObjectName("remove_data_type_watch")
        self.available_data_type_list = QtWidgets.QListView(self.select_data_frame)
        self.available_data_type_list.setGeometry(QtCore.QRect(10, 10, 151, 101))
        self.available_data_type_list.setObjectName("available_data_type_list")
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

        self.disconnect = True
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

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
            print(self.disconnect)

        else:
            self.connect_or_disconnect_signal.emit('disconnect')
            self.connect_button.setText(self._translate("Dialog", "Connect"))
            self.disconnect = True
            print(self.disconnect)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

