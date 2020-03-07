from PyQt5 import QtCore, QtGui, QtWidgets
from AnalyzePage import AnalyzePage
from CollectPage import CollectPage
from ControlPage import ControlPage
from ConnectPage import ConnectPage
from OscilloscopePage import OscilloscopePage
import json

class MachineActionPage(QtWidgets.QDialog):
    def __init__(self, backend, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.backend = backend
        self.backend.node_type_received.connect(self.nodeTypeReceiveHandler)

        self.connect_page = ConnectPage(self.backend, self)
        self.control_page = ControlPage(self.backend, self)
        self.collect_page = CollectPage(self.backend, self)
        self.oscilloscope_page = OscilloscopePage(self.backend, self)
        #self.analyze_page = AnalyzePage(self.backend, self)

        self.connect_tab = QtWidgets.QListWidgetItem("Connect")
        self.control_tab = QtWidgets.QListWidgetItem("Control")
        self.collect_tab = QtWidgets.QListWidgetItem("Collect")
        self.oscilloscope_tab = QtWidgets.QListWidgetItem("Oscilloscope")
        #self.analyze_tab = QtWidgets.QListWidgetItem("Analyze")

        self.tab_list = QtWidgets.QListWidget()
        self.tab_list.addItem(self.connect_tab)
        self.tab_list.addItem(self.control_tab)
        self.tab_list.addItem(self.collect_tab)
        self.tab_list.addItem(self.oscilloscope_tab)
        #self.tab_list.addItem(self.analyze_tab)
        
        self.panel_widget_layout = QtWidgets.QVBoxLayout()
        self.panel_widget_layout.setAlignment(QtCore.Qt.AlignTop)
        self.panel_widget_layout.setContentsMargins(QtCore.QMargins(0, 0 , 0, 0))
        self.panel_widget_layout.addWidget(self.tab_list)
        
        self.panel_widget = QtWidgets.QDialog()
        self.panel_widget.setLayout(self.panel_widget_layout)

        self.main_workspace_stack = QtWidgets.QStackedLayout()
        self.main_workspace_stack.addWidget(self.connect_page)
        self.main_workspace_stack.addWidget(self.control_page)
        self.main_workspace_stack.addWidget(self.collect_page)
        self.main_workspace_stack.addWidget(self.oscilloscope_page)
        #self.main_workspace_stack.addWidget(self.analyze_page)

        self.tab_list.currentRowChanged.connect(self.main_workspace_stack.setCurrentIndex)

        self.main_workspace = QtWidgets.QDialog()
        self.main_workspace.setLayout(self.main_workspace_stack)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_layout.addWidget(self.panel_widget, stretch=1)
        self.main_layout.addWidget(self.main_workspace, stretch=10)

        self.setLayout(self.main_layout)
        self.type_dict = {}
        #self.list_of_node_received_slot(['test_node'])

    def list_of_node_received_slot(self, list_of_node):
        for node in list_of_node:
            node_tree_item = QtWidgets.QTreeWidgetItem(self.node_tree, [node])
            self.node_tree.addTopLevelItem(node_tree_item)
            self.type_dict[node] = []
        
        for node in self.type_dict:
            self.backend.getNodeType(node)

    def nodeTypeReceiveHandler(self, node_name, node_type):
        if node_name in self.type_dict:
            self.type_dict[node_name] = node_type
