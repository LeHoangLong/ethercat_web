from PyQt5 import QtCore, QtGui, QtWidgets
from backend import AppBackend, WorkstationBackend
from enum import Enum

class MachineActionPage(QtWidgets.QDialog):
    class ConnectPage(QtWidgets.QDialog):
        def __init__(self, backend, parent=None):
            super().__init__(parent)
            self.backend = backend
            
            self.main_layout = QtWidgets.QVBoxLayout()
            self.setLayout(self.main_layout)
            

            self.connect_button = QtWidgets.QPushButton("Connect")

            self.status = QtWidgets.QLabel("Status: disconnected")

            self.button_layout = QtWidgets.QHBoxLayout()

            self.button_layout.addWidget(self.connect_button, stretch=1)
            self.button_layout.addWidget(self.status, stretch=5)

            self.main_layout.setAlignment(QtCore.Qt.AlignTop)
            self.main_layout.addLayout(self.button_layout)

            self.backend.update_connection_status_signal.connect(self.backend_connection_status_update_slot)
            self.connect_button.pressed.connect(self.connection_button_pressed_slot)

        def connection_button_pressed_slot(self):
            if self.connect_button.text() == 'Connect':
                self.backend.connection_req.emit(self.backend.ConnectionRequest.CONNECT)
            if self.connect_button.text() == 'Cancel':
                self.backend.connection_req.emit(self.backend.ConnectionRequest.CANCEL)
            if self.connect_button.text() == 'Disconnect':
                self.backend.connection_req.emit(self.backend.ConnectionRequest.DISCONNECT)

        def backend_connection_status_update_slot(self, status):
            if status == self.backend.ConnectionStatus.DISCONNECTED:
                self.status.setText("Status: disconnected")
                self.connect_button.setText("Connect")
            elif status == self.backend.ConnectionStatus.CONNECTING:
                self.status.setText("Status: connecting")
                self.connect_button.setText("Cancel")
            elif status == self.backend.ConnectionStatus.CONNECTED:
                self.status.setText("Status: connected")
                self.connect_button.setText("Disconnect")

    class ControlPage(QtWidgets.QDialog):
        def __init__(self, backend, parent=None):
            super().__init__(parent)
            self.setStyleSheet('background-color: grey;')

    class CollectPage(QtWidgets.QDialog):
        def __init__(self, backend, parent=None):
            super().__init__(parent)
            self.setStyleSheet('background-color: grey;')

    class AnalyzePage(QtWidgets.QDialog):
        def __init__(self, backend, parent=None):
            super().__init__(parent)
            self.setStyleSheet('background-color: grey;')

    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend

        self.connect_tab = QtWidgets.QListWidgetItem("Connect")
        self.control_tab = QtWidgets.QListWidgetItem("Control")
        self.collect_tab = QtWidgets.QListWidgetItem("Collect")
        self.analyze_tab = QtWidgets.QListWidgetItem("Analyze")

        self.tab_list = QtWidgets.QListWidget()
        self.tab_list.addItem(self.connect_tab)
        self.tab_list.addItem(self.control_tab)
        self.tab_list.addItem(self.collect_tab)
        self.tab_list.addItem(self.analyze_tab)

        self.node_tree = QtWidgets.QTreeWidget()

        self.panel_widget_layout = QtWidgets.QVBoxLayout()
        self.panel_widget_layout.setAlignment(QtCore.Qt.AlignTop)
        self.panel_widget_layout.setContentsMargins(QtCore.QMargins(0, 0 , 0, 0))
        self.panel_widget_layout.addWidget(self.tab_list, stretch=1)
        self.panel_widget_layout.addWidget(self.node_tree, stretch=7)
        
        self.panel_widget = QtWidgets.QDialog()
        self.panel_widget.setLayout(self.panel_widget_layout)

        self.connect_page = self.ConnectPage(self.backend)
        self.control_page = self.ControlPage(self.backend)
        self.collect_page = self.CollectPage(self.backend)
        self.analyze_page = self.AnalyzePage(self.backend)

        self.main_workspace_stack = QtWidgets.QStackedLayout()
        self.main_workspace_stack.addWidget(self.connect_page)
        self.main_workspace_stack.addWidget(self.control_page)
        self.main_workspace_stack.addWidget(self.collect_page)
        self.main_workspace_stack.addWidget(self.analyze_page)

        self.tab_list.currentRowChanged.connect(self.main_workspace_stack.setCurrentIndex)

        self.main_workspace = QtWidgets.QDialog()
        self.main_workspace.setLayout(self.main_workspace_stack)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_layout.addWidget(self.panel_widget, stretch=1)
        self.main_layout.addWidget(self.main_workspace, stretch=10)

        self.setLayout(self.main_layout)

class AddressableButton(QtWidgets.QPushButton):
    def __init__(self, name, address, QIcon=None, str='', parent=None):
        if (QIcon == None):
            super().__init__(str, parent=parent)
        else:
            super().__init__(QIcon, str, parent=parent)

        self.name = name
        self.address = address

class MachineListPage(QtWidgets.QDialog):
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
            
            new_button = AddressableButton(machine['name'], machine['address'])
            new_button.setLayout(new_button_layout)
            new_button.setFixedHeight(70)

            row_layout = QtWidgets.QVBoxLayout()
            row_layout.addWidget(new_button)

            new_button_container = QtWidgets.QWidget()
            new_button_container.setLayout(row_layout)
            
            self.machine_list_layout.addWidget(new_button_container)
            new_button.pressed.connect(self.button_pressed)

class App(QtWidgets.QDialog):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.backend = AppBackend()

        self.machine_page = MachineListPage()

        list_of_workstation = self.backend.getWorkstationList()

        for i, workstation in enumerate(list_of_workstation):
            self.machine_page.addMachine("machine_" + str(i), workstation['jid'], workstation['status'])
        
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.machine_page, "machine")
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab_slot)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)
        
        self.machine_page.open_page_signal.connect(self.open_tab_slot)
        self.opened_tab_name_list = []


    def open_tab_slot(self, name, address):
        if name not in self.opened_tab_name_list:
            self.work_tab = MachineActionPage(self.backend.createWorkstationBackend(address))
            self.tab_widget.addTab(self.work_tab, name)
            self.opened_tab_name_list.append(name)
        idx = 0

        for i, tab_name in enumerate(self.opened_tab_name_list):
            if tab_name == name:
                idx = i
                break

        self.tab_widget.setCurrentIndex(idx + 1)

    def close_tab_slot(self, idx):
        if idx != 0 and idx != -1:
            self.tab_widget.removeTab(idx)
            self.opened_tab_name_list.remove(self.opened_tab_name_list[idx - 1])

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = App()
    main_window.showMaximized()
    
    sys.exit(app.exec_())