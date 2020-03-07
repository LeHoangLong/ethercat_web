from PyQt5 import QtWidgets, QtCore

class LabeledComboBox(QtWidgets.QWidget):
    def __init__(self, label_text, parent=None):
        super().__init__(parent)

        self.label = QtWidgets.QLabel(label_text)
        
        self.combo_box = QtWidgets.QComboBox()

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.label, stretch=1)
        self.main_layout.addWidget(self.combo_box, stretch=15)
        self.setLayout(self.main_layout)
    
    def currentText(self):
        return self.combo_box.currentText()
    
    def addItems(self, list_type):
        self.combo_box.addItems(list_type)