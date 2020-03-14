from PyQt5 import QtWidgets, QtCore

class ControlPage(QtWidgets.QDialog):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.main_layout = QtWidgets.QVBoxLayout()
        self.run_button = QtWidgets.QPushButton('run')
        self.main_layout.addWidget(self.run_button)
        self.setLayout(self.main_layout)
        self.run_button.clicked.connect(self.runButtonClickedHandler)

        self.state_list_widget = QtWidgets.QListWidget()
        self.main_layout.addWidget(self.state_list_widget)

        self.backend.program_state_updated_signal.connect(self.stateUpdateHandler)
        self.stateUpdateHandler()

    def runButtonClickedHandler(self):
        self.backend.sendControlSignal('run', value='1')

    def stateUpdateHandler(self):
        try:
            current_state = self.backend.getProgramState()
            self.state_list_widget.clear()
            for state_name, state_val in current_state.items():
                state_str = state_name + ' : ' + state_val
                state_widget_item = QtWidgets.QListWidgetItem(state_str)
                self.state_list_widget.addItem(state_widget_item)
        except Exception as e:
            print(e)
            pass

