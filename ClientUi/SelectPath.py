from PyQt5 import QtWidgets, QtCore

class SelectPath(QtWidgets.QWidget):
    selected_path_changed_signal = QtCore.pyqtSignal()

    def __init__(self, button_name, initial_path='', parent=None):
        super().__init__(parent)
        self.selected_path = initial_path
        self.save_location_button = QtWidgets.QPushButton(button_name)
        self.save_location_button.clicked.connect(self.chooseTargetFolderButtonClickHandler)
        self.current_location_text = QtWidgets.QLabel(self.selected_path)
        self.current_location_text.setStyleSheet('border-width: 1px; border-style: solid; border-color: black;')
        self.current_location_text.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.save_location_button, stretch=1)
        self.main_layout.addWidget(self.current_location_text, stretch=10)
        
        self.setLayout(self.main_layout)

        self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        
    def chooseTargetFolderButtonClickHandler(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder")
        if path != '':
            self.selected_path = path
        if self.selected_path != self.current_location_text.text():
            self.current_location_text.setText(self.selected_path)
            self.selected_path_changed_signal.emit()
            
    def getSelectedPath(self):
        return self.selected_path