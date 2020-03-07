from PyQt5 import QtWidgets, QtCore

class DualButtonWidget(QtWidgets.QWidget):
    def __init__(self, button_1_name, button_2_name, direction=0, parent=None):
        super().__init__(parent)
        self.button_1 = QtWidgets.QPushButton(button_1_name)
        self.button_2 = QtWidgets.QPushButton(button_2_name)
        if direction == 0:
            self.main_layout = QtWidgets.QHBoxLayout()
        else:
            self.main_layout = QtWidgets.QVBoxLayout()

        self.main_layout.addWidget(self.button_1)
        self.main_layout.addWidget(self.button_2)
        self.setLayout(self.main_layout)
        self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
