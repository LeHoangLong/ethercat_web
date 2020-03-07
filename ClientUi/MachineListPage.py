from PyQt5 import QtCore, QtGui, QtWidgets

class MachineListPage(QtWidgets.QDialog):

    class AddressableButton(QtWidgets.QPushButton):
        def __init__(self, name, address, QIcon=None, str='', parent=None):
            if (QIcon == None):
                super().__init__(str, parent=parent)
            else:
                super().__init__(QIcon, str, parent=parent)

            self.name = name
            self.address = address

    open_page_signal = QtCore.pyqtSignal(str, str, name='open_page_signal')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.machine_list = []
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)
        self.machine_list_container = QtWidgets.QDialog()
        self.machine_list_layout = QtWidgets.QVBoxLayout()
        self.machine_list_layout.setContentsMargins(0, 50, 0, 100)
        self.machine_list_layout.setSpacing(10)
        self.machine_list_layout.setAlignment(QtCore.Qt.AlignTop)
        self.machine_list_container.setLayout(self.machine_list_layout)
        self.scroll_area.setWidget(self.machine_list_container)
        self.scroll_area.setLayout(QtWidgets.QHBoxLayout())
        self.scroll_area.setWidgetResizable(True)
        self.updateList()

    def button_pressed(self):
        self.open_page_signal.emit(self.sender().name, self.sender().address)

    def addMachine(self, machine_name, address, status):
        found = False
        for machine in self.machine_list:
            if machine['name'] == machine_name:
                found = True
                break
        if found == False:
            self.machine_list.append({
                'name': machine_name,
                'address': address,
                'status': status
            })
            self.updateList()

    def updateMachineStatus(self, machine_name, machine_address, status):
        found = False
        found_machine = None
        for machine in self.machine_list:
            if machine['name'] == machine_name and machine['address'] == machine_address:
                found_machine = machine
                found = True
                break
        if found == True:
            found_machine['status'] = status
            self.updateList()

    
    def updateList(self):
        for i in reversed(range(self.machine_list_layout.count())):
            self.machine_list_layout.itemAt(i).widget().setParent(None)
        for machine in self.machine_list:
            machine_name_label = QtWidgets.QLabel('name: ' + machine['name'])
            machine_name_label.setMargin(0)
            machine_name_label.setFixedHeight(20)
            machine_address_label = QtWidgets.QLabel('address: ' + machine['address'])
            machine_address_label.setMargin(0)
            machine_address_label.setFixedHeight(20)
            machine_status_label = QtWidgets.QLabel('status: ' + machine['status'])
            machine_status_label.setMargin(0)
            machine_status_label.setFixedHeight(20)

            new_button_layout = QtWidgets.QVBoxLayout()
            new_button_layout.setSpacing(0)
            new_button_layout.setContentsMargins(QtCore.QMargins(-1, 0, -1, 0))
            new_button_layout.addWidget(machine_name_label)
            new_button_layout.addWidget(machine_address_label)
            new_button_layout.addWidget(machine_status_label)
            
            new_button = self.AddressableButton(machine['name'], machine['address'])
            new_button.setLayout(new_button_layout)
            new_button.setFixedHeight(70)

            row_layout = QtWidgets.QVBoxLayout()
            row_layout.addWidget(new_button)

            new_button_container = QtWidgets.QWidget()
            new_button_container.setLayout(row_layout)
            
            self.machine_list_layout.addWidget(new_button_container)
            new_button.pressed.connect(self.button_pressed)
