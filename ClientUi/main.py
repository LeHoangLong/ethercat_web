from PyQt5 import QtCore, QtGui, QtWidgets
from backend import AppBackend, WorkstationBackend
from MachineActionPage import MachineActionPage
from MachineListPage import MachineListPage
from AnalyzePage import AnalyzePage
from enum import Enum
import json

class App(QtWidgets.QDialog):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.backend = AppBackend()

        self.machine_page = MachineListPage()
        self.analyze_page = AnalyzePage()

        list_of_workstation = self.backend.getWorkstationList()
        for i, workstation in enumerate(list_of_workstation):
            self.machine_page.addMachine("machine_" + str(i), workstation['jid'], workstation['status'])
        
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.machine_page, "machine")
        self.tab_widget.addTab(self.analyze_page, "analyze")
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab_slot)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)
        
        self.machine_page.open_page_signal.connect(self.open_tab_slot)
        self.opened_tab_name_list = []

        self.backend.presence_updated_signal.connect(self.presenceUpdateHandler)

    def presenceUpdateHandler(self):
        list_of_workstation = self.backend.getWorkstationList()

        for i, workstation in enumerate(list_of_workstation):
            self.machine_page.updateMachineStatus("machine_" + str(i), workstation['jid'], workstation['status'])
        
        pass

    def open_tab_slot(self, name, address):
        if name not in self.opened_tab_name_list:
            self.work_tab = MachineActionPage(self.backend.createWorkstationBackend(address), name, self)
            #self.work_tab = MachineActionPage(None, name, self)
            self.tab_widget.addTab(self.work_tab, name)
            self.opened_tab_name_list.append(name)
        idx = 0

        for i, tab_name in enumerate(self.opened_tab_name_list):
            if tab_name == name:
                idx = i
                break

        self.tab_widget.setCurrentIndex(idx + 2)

    def close_tab_slot(self, idx):
        if idx != 0 and idx != -1 and idx != 1:
            self.tab_widget.removeTab(idx)
            self.opened_tab_name_list.remove(self.opened_tab_name_list[idx - 1])

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main_window = App()
    main_window.showMaximized()
    
    sys.exit(app.exec_())