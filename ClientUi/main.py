from PyQt5 import QtCore, QtGui, QtWidgets
from backend import AppBackend, WorkstationBackend
from enum import Enum
import json

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

    class CollectPage(QtWidgets.QWidget):
        class GenericCollectPage(QtWidgets.QWidget):
            def __init__(self, node_name, backend, parent=None):
                super().__init__(parent)
                self.parent = parent
                #self.setStyleSheet('background-color: green')
                self.backend = backend
                self.node_name = node_name

                #start trigger set up widget
                self.start_trigger_add_button = QtWidgets.QPushButton("Add start trigger")
                self.start_trigger_add_button.clicked.connect(self.addStartTriggerButtonClickedHandler)
                self.start_trigger_remove_button = QtWidgets.QPushButton("Remove start trigger")

                self.start_trigger_add_remove_button_layout = QtWidgets.QHBoxLayout()
                self.start_trigger_add_remove_button_layout.addWidget(self.start_trigger_add_button)
                self.start_trigger_add_remove_button_layout.addWidget(self.start_trigger_remove_button)

                self.start_trigger_condition_list = QtWidgets.QListWidget()

                self.start_trigger_label = QtWidgets.QLabel("Start trigger")


                self.start_trigger_layout = QtWidgets.QVBoxLayout()
                self.start_trigger_layout.addWidget(self.start_trigger_label)
                self.start_trigger_layout.addWidget(self.start_trigger_condition_list)
                self.start_trigger_layout.addLayout(self.start_trigger_add_remove_button_layout)
                
                self.start_trigger_widget = QtWidgets.QWidget()
                self.start_trigger_widget.setLayout(self.start_trigger_layout)
                ################################################################################
                
                #end trigger set up widget
                self.end_trigger_add_button = QtWidgets.QPushButton("Add start trigger")
                self.end_trigger_remove_button = QtWidgets.QPushButton("Remove start trigger")

                self.end_trigger_add_remove_button_layout = QtWidgets.QHBoxLayout()
                self.end_trigger_add_remove_button_layout.addWidget(self.end_trigger_add_button)
                self.end_trigger_add_remove_button_layout.addWidget(self.end_trigger_remove_button)

                self.end_trigger_condition_list = QtWidgets.QListWidget()

                self.end_trigger_label = QtWidgets.QLabel("End trigger")

                self.end_trigger_layout = QtWidgets.QVBoxLayout()
                self.end_trigger_layout.addWidget(self.end_trigger_label)
                self.end_trigger_layout.addWidget(self.end_trigger_condition_list)
                self.end_trigger_layout.addLayout(self.end_trigger_add_remove_button_layout)
                
                self.end_trigger_widget = QtWidgets.QWidget()
                self.end_trigger_widget.setLayout(self.end_trigger_layout)
                ################################################################################


                #trigger set up widget
                self.trigger_setup_layout = QtWidgets.QVBoxLayout()
                self.trigger_setup_layout.addWidget(self.start_trigger_widget)
                self.trigger_setup_layout.addWidget(self.end_trigger_widget)

                self.trigger_setup_widget = QtWidgets.QWidget()
                self.trigger_setup_widget.setLayout(self.trigger_setup_layout)
                ################################################################################

                #save folder widget
                try:
                    metadata_file = open("meta.txt", "r")
                    json_data_str =  metadata_file.read()
                    json_data = json.loads(json_data_str)
                    if self.parent.parent.name in json_data:
                        self.save_location_path = json_data[self.parent.parent.name]['save_location']
                    else:
                        self.save_location_path = ""
                except Exception:
                    self.save_location_path = ""

                self.save_location_button = QtWidgets.QPushButton("Choose folder")
                self.save_location_button.clicked.connect(self.chooseTargetFolderButtonClickHandler)
                self.save_location_button.setStyleSheet('background-color: red')
                self.current_location_text = QtWidgets.QLabel(self.save_location_path)
                self.current_location_text.setStyleSheet('border-width: 1px; border-style: solid; border-color: black;')
                self.current_location_text.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                
                self.select_location_layout = QtWidgets.QHBoxLayout()
                self.select_location_layout.addWidget(self.current_location_text, stretch=8)
                self.select_location_layout.addWidget(self.save_location_button, stretch=1)
                self.select_location_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                
                self.select_location_widget = QtWidgets.QWidget()
                self.select_location_widget.setLayout(self.select_location_layout)
                self.select_location_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                ################################################################################

                self.collect_data_label = QtWidgets.QLabel("Available collect data")
                
                self.collect_data_list = QtWidgets.QListWidget()
                
                self.add_collect_data_button = QtWidgets.QPushButton("Add")
                self.add_collect_data_button.clicked.connect(self.addDataCollectorButtonClickedHandler)
                self.remove_collect_data_button = QtWidgets.QPushButton("Remove")

                self.add_and_remove_collect_data_layout = QtWidgets.QHBoxLayout()
                self.add_and_remove_collect_data_layout.addWidget(self.add_collect_data_button)
                self.add_and_remove_collect_data_layout.addWidget(self.remove_collect_data_button)
                self.add_and_remove_collect_data_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                self.add_and_remove_collect_data_widget = QtWidgets.QWidget()
                self.add_and_remove_collect_data_widget.setLayout(self.add_and_remove_collect_data_layout)
                self.add_and_remove_collect_data_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                self.collect_data_layout = QtWidgets.QVBoxLayout()
                self.collect_data_layout.addWidget(self.collect_data_label)
                self.collect_data_layout.addWidget(self.collect_data_list)
                self.collect_data_layout.addWidget(self.add_and_remove_collect_data_widget)
                self.collect_data_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                self.collect_data_widget = QtWidgets.QWidget()
                self.collect_data_widget.setLayout(self.collect_data_layout)
                self.collect_data_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                self.collect_data_and_save_layout = QtWidgets.QVBoxLayout()
                self.collect_data_and_save_layout.addWidget(self.collect_data_widget)
                self.collect_data_and_save_layout.addWidget(self.select_location_widget)
                self.collect_data_and_save_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                self.collect_data_and_save_widget = QtWidgets.QWidget()
                self.collect_data_and_save_widget.setLayout(self.collect_data_and_save_layout)
                self.collect_data_and_save_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                self.workspace_layout = QtWidgets.QHBoxLayout()
                self.workspace_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                self.workspace_layout.addWidget(self.collect_data_and_save_widget)
                self.workspace_layout.addWidget(self.trigger_setup_widget)

                self.workspace_widget = QtWidgets.QWidget()
                self.workspace_widget.setLayout(self.workspace_layout)

                self.apply_button = QtWidgets.QPushButton("Apply")
                self.apply_button.clicked.connect(self.applyClickedHandler)

                self.is_collecting = False
                self.start_button = QtWidgets.QPushButton("Start")
                self.start_button.clicked.connect(self.startClickedHandler)

                self.main_layout = QtWidgets.QVBoxLayout()
                self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                self.main_layout.addWidget(self.workspace_widget)
                self.main_layout.addWidget(self.apply_button)
                self.main_layout.addWidget(self.start_button)

                self.setLayout(self.main_layout)
                
                self.pending_data = {}

            def availableCollectDataAddHandler(self, data_dict):
                self.collect_data_list.clear()
                for data in data_dict:
                    full_name = self.node_name + '/' + data
                    if full_name not in self.pending_data:
                        data_widget = QtWidgets.QListWidgetItem(full_name)
                        self.collect_data_list.addItem(data_widget)
                        self.pending_data[full_name] = {
                            'collect_type': data_dict[data]['collect_type'],
                            'data_type': data_dict[data]['data_type']
                        }

            def chooseTargetFolderButtonClickHandler(self):
                path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder")
                if path != '':
                    self.save_location_path = path
                self.current_location_text.setText(self.save_location_path)

            def applyClickedHandler(self):
                meta_data_file = open("meta.txt", "w")
                json_data = {
                    self.parent.parent.name: {
                        "save_location": self.save_location_path,
                        "data_collect_list": self.pending_data
                    }
                }
                
                meta_data_file.write(json.dumps(json_data))
                meta_data_file.close()

                for data_name, data_info in self.pending_data.items():
                    self.backend.addDataCollector(data_name, data_info['collect_type'], data_info['data_type'])
                self.pending_data = {}

            def startClickedHandler(self):
                self.is_collecting = not self.is_collecting

                if self.is_collecting:
                    self.backend.startDataCollection()
                    self.start_button.setText("Stop")
                else:
                    self.backend.stopDataCollection()
                    self.start_button.setText("Start")

            class AddDataCollectorDialog(QtWidgets.QDialog):
                add_data_signal = QtCore.pyqtSignal(dict)

                def __init__(self, backend, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle("Add data")
                    self.backend = backend
                    

                    self.main_layout = QtWidgets.QVBoxLayout()

                    self.setLayout(self.main_layout)

                    self.tree_header = QtWidgets.QTreeWidgetItem(['Available data'])

                    self.added_data_list = {}

                    self.tree_item_list = []
                    self.tree_widget = QtWidgets.QTreeWidget()
                    self.tree_widget.setHeaderItem(self.tree_header)
                    self.tree_widget.itemChanged.connect(self.treeChangedHandler)
                    
                    self.available_data_tree = self.backend.getAvailableCollectData()
                    for node in self.available_data_tree:
                        self.addNodetoTree(self.tree_widget, node)

                    self.main_layout.addWidget(self.tree_widget)

                    self.ok_button = QtWidgets.QPushButton("OK")
                    self.ok_button.clicked.connect(self.okButtonHandler)
                    self.main_layout.addWidget(self.ok_button)


                def treeChangedHandler(self, item, column):
                    path = item.text(0)
                    parent = item.parent()
                    while parent != self.tree_widget and parent != None:
                        path = parent.text(0) + '/' + path
                        parent = parent.parent()

                    if item.checkState(0) == QtCore.Qt.Checked:
                        self.added_data_list[path] = {
                            'collect_type': 'DEFAULT',
                            'data_type': 'int'
                        }
                    else:
                        if path in self.added_data_list:
                            del self.added_data_list[path]

                def okButtonHandler(self):
                    self.add_data_signal.emit(self.added_data_list)
                    self.close()

                def addNodetoTree(self, tree, node):
                    child = QtWidgets.QTreeWidgetItem(tree)
                    child.setText(0, node['name'])
                    if node['type'] == 'list':
                        node_list = node['data']
                        for node in node_list:
                            self.addNodetoTree(child, node)
                    else:
                        child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                        child.setCheckState(0, QtCore.Qt.Unchecked)

                    self.tree_item_list.append(child)


            def addDataCollectorButtonClickedHandler(self):
                self.dialog = self.AddDataCollectorDialog(self.backend)
                self.dialog.add_data_signal.connect(self.availableCollectDataAddHandler)
                self.dialog.setModal(True)
                self.dialog.show()

            class AddDataTriggerDialog(QtWidgets.QDialog):
                class TreeWidgetItemWrapper(QtWidgets.QTreeWidgetItem):
                    def __init__(self, obj=None, callback=None, parent=None):
                        super().__init__(parent)
                        self.callback_obj = obj
                        self.callback_func = callback
                        pass

                def __init__(self, backend, name, parent=None):
                    super().__init__(parent)
                    self.backend = backend
                    self.parent = parent
                    self.name = name
                    self.setModal(True)
                    self.main_layout = QtWidgets.QHBoxLayout()
                    self.setLayout(self.main_layout)

                    self.tree_header = QtWidgets.QTreeWidgetItem(['Available data'])

                    self.condition_A = QtWidgets.QTreeWidget()
                    self.condition_A.setHeaderItem(self.tree_header)
                    self.condition_A.itemClicked.connect(self.conditionATreeChangedHandler)
                    self.condition_A.itemDoubleClicked.connect(self.conditionATreeDoubleClickedHandler)

                    self.condition_B = QtWidgets.QTreeWidget()
                    self.condition_B.setHeaderItem(self.tree_header)
                    self.condition_B.itemClicked.connect(self.conditionBTreeChangedHandler)
                    self.condition_B.itemDoubleClicked.connect(self.conditionBTreeDoubleClickedHandler)

                    self.condition_item_list = []

                    self.comparison_box = QtWidgets.QComboBox()
                    self.comparison_box.addItem(">")
                    self.comparison_box.addItem(">=")
                    self.comparison_box.addItem("==")
                    self.comparison_box.addItem("!=")
                    self.comparison_box.addItem("<=")
                    self.comparison_box.addItem("<")

                    self.comparison_widget = QtWidgets.QWidget()
                    self.comparison_layout = QtWidgets.QVBoxLayout()
                    self.comparison_layout.addWidget(self.comparison_box)
                    self.comparison_layout.addStretch(1)
                    self.comparison_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                    
                    self.comparison_widget.setLayout(self.comparison_layout)
                    self.comparison_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                    self.available_data_tree = self.backend.getAvailableCollectData()

                    num_of_sample_node = {
                        'type': 'int',
                        'name': 'Number of samples'
                    }

                    constant_node = {
                        'type': 'int',
                        'name': 'Constant: 0'
                    }

                    self.const_A = 0
                    self.condition_A_item_list = []
                    self.addNodetoConditionTree(self.condition_A, num_of_sample_node, self.condition_A_item_list)
                    self.addNodetoConditionTree(self.condition_A, constant_node, self.condition_A_item_list, self.constantClickedHandler, self.const_A)
                    self.selected_A = None

                    for node in self.available_data_tree:
                        self.addNodetoConditionTree(self.condition_A, node, self.condition_A_item_list)

                    self.const_B = 0
                    self.condition_B_item_list = []
                    self.addNodetoConditionTree(self.condition_B, num_of_sample_node, self.condition_B_item_list)
                    self.addNodetoConditionTree(self.condition_B, constant_node, self.condition_B_item_list, self.constantClickedHandler, self.const_B)
                    self.selected_B = None

                    for node in self.available_data_tree:
                        self.addNodetoConditionTree(self.condition_B, node, self.condition_B_item_list)

                    self.ok_button = QtWidgets.QPushButton('OK')
                    self.ok_button.clicked.connect(self.okButtonClickedHandler)
                    self.ok_button_widget = QtWidgets.QWidget()
                    self.ok_button_layout = QtWidgets.QVBoxLayout()
                    self.ok_button_layout.addWidget(self.ok_button)
                    self.ok_button_layout.addStretch(1)
                    self.ok_button_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
                    
                    self.ok_button_widget.setLayout(self.ok_button_layout)
                    self.ok_button_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

                    self.main_layout.addWidget(self.condition_A)
                    self.main_layout.addWidget(self.comparison_widget)
                    self.main_layout.addWidget(self.condition_B)
                    self.main_layout.addWidget(self.ok_button_widget)
                    self.main_layout.setAlignment(QtCore.Qt.AlignTop)

                def okButtonClickedHandler(self):
                    self.backend.addTrigger(self.selected_A.text(0), self.selected_B.text(0), self.comparison_box.currentText(), self.name)
                    self.close()

                def conditionATreeChangedHandler(self, item, column):
                    if item.childCount() == 0:
                        self.clearCheckState(self.condition_A_item_list)
                        item.setCheckState(0, QtCore.Qt.Checked)
                        self.selected_A = item

                def conditionBTreeChangedHandler(self, item, column):
                    if item.childCount() == 0:
                        self.clearCheckState(self.condition_B_item_list)
                        item.setCheckState(0, QtCore.Qt.Checked)
                        self.selected_B = item

                def conditionATreeDoubleClickedHandler(self, item, column):
                    if item.callback_func != None:
                        item.callback_func(item, item.callback_obj, 'DOUBLE_CLICKED')

                def conditionBTreeDoubleClickedHandler(self, item, column):
                    if item.callback_func != None:
                        item.callback_func(item, item.callback_obj, 'DOUBLE_CLICKED')

                def constantClickedHandler(self, item, callback_obj, callback_type):
                    if callback_type == 'DOUBLE_CLICKED':
                        value, ok = QtWidgets.QInputDialog.getDouble(self, 'Constant value', 'Enter number')
                        if ok:
                            item.setText(0, 'Constant: ' + str(value))

                def clearCheckState(self, item_list):
                    for item in item_list:
                        if item.childCount() == 0:
                            item.setCheckState(0, QtCore.Qt.Unchecked)

                def addNodetoConditionTree(self, tree, node, condition_item_list, callback=None, callback_obj=None):
                    child = self.TreeWidgetItemWrapper(callback_obj, callback, tree)
                    child.setText(0, node['name'])
                    if node['type'] == 'list':
                        node_list = node['data']
                        for node in node_list:
                            self.addNodetoConditionTree(child, node, condition_item_list)
                    else:
                        child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                        child.setCheckState(0, QtCore.Qt.Unchecked)

                    condition_item_list.append(child)

            def addStartTriggerButtonClickedHandler(self):
                self.dialog = self.AddDataTriggerDialog(self.backend, 'START_TRIGGER')
                self.dialog.show()


        class EthercatCollectPage(QtWidgets.QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.main_layout = QtWidgets.QVBoxLayout()
                self.setStyleSheet('background-color: blue')

        def __init__(self, backend, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.main_widget = QtWidgets.QDialog(self)
            self.backend = backend
            self.main_layout = QtWidgets.QVBoxLayout(self)
            self.setLayout(self.main_layout)
            self.view_as_label = QtWidgets.QLabel("View as")
            self.view_as_combo_box = QtWidgets.QComboBox()
            self.view_as_layout = QtWidgets.QHBoxLayout()
            self.view_as_layout.addWidget(self.view_as_label, stretch=1)
            self.view_as_layout.addWidget(self.view_as_combo_box, stretch=15)
            self.view_as_widget = QtWidgets.QWidget(self)
            self.view_as_widget.setLayout(self.view_as_layout)
            self.main_layout.addWidget(self.view_as_widget, alignment=QtCore.Qt.AlignTop, stretch=1)
            self.current_item = None
            self.view_as_combo_box.currentTextChanged.connect(self.typeViewSelectHandler)
            
        def itemSelectHandler(self, item, column):
            if item.text(column) != self.current_item:
                type_list = self.parent.type_dict[item.text(0)]
                
                self.view_as_combo_box.clear()
                self.current_node_name = item.text(0)
                
                first_type = type_list[0]
                self.typeViewSelectHandler(first_type)

                for type_element in type_list:
                    self.view_as_combo_box.addItem(type_element)


        
        def typeViewSelectHandler(self, current_type):
            self.main_layout.removeWidget(self.main_widget)
            self.main_widget.setParent(None)
            del self.main_widget
            if current_type == 'GENERIC':
                self.main_widget = self.GenericCollectPage(self.current_node_name, self.backend, self)
            else:
                self.main_widget = self.EthercatCollectPage()
            self.main_layout.addWidget(self.main_widget, stretch=20)


    class ControlPage(QtWidgets.QDialog):
        def __init__(self, backend, parent=None):
            super().__init__(parent)
            self.setStyleSheet('background-color: grey;')

    class AnalyzePage(QtWidgets.QDialog):
        def __init__(self, backend, parent=None):
            super().__init__(parent)
            self.setStyleSheet('background-color: grey;')

    def __init__(self, backend, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.backend = backend
        self.backend.all_node_received_signal.connect(self.list_of_node_received_slot)
        self.backend.node_type_received.connect(self.nodeTypeReceiveHandler)

        self.connect_page = self.ConnectPage(self.backend, self)
        self.control_page = self.ControlPage(self.backend, self)
        self.collect_page = self.CollectPage(self.backend, self)
        self.analyze_page = self.AnalyzePage(self.backend, self)

        self.connect_tab = QtWidgets.QListWidgetItem("Connect")
        self.control_tab = QtWidgets.QListWidgetItem("Control")
        self.collect_tab = QtWidgets.QListWidgetItem("Collect")
        self.analyze_tab = QtWidgets.QListWidgetItem("Analyze")

        self.tab_list = QtWidgets.QListWidget()
        self.tab_list.addItem(self.connect_tab)
        self.tab_list.addItem(self.control_tab)
        self.tab_list.addItem(self.collect_tab)
        self.tab_list.addItem(self.analyze_tab)

        self.node_tree_header = QtWidgets.QTreeWidgetItem(['List of nodes'])
        
        self.node_tree = QtWidgets.QTreeWidget()
        self.node_tree.setHeaderItem(self.node_tree_header)
        self.node_tree.itemActivated.connect(self.collect_page.itemSelectHandler)

        self.panel_widget_layout = QtWidgets.QVBoxLayout()
        self.panel_widget_layout.setAlignment(QtCore.Qt.AlignTop)
        self.panel_widget_layout.setContentsMargins(QtCore.QMargins(0, 0 , 0, 0))
        self.panel_widget_layout.addWidget(self.tab_list, stretch=1)
        self.panel_widget_layout.addWidget(self.node_tree, stretch=7)
        
        self.panel_widget = QtWidgets.QDialog()
        self.panel_widget.setLayout(self.panel_widget_layout)

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
        self.type_dict = {}

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

        self.backend.presence_updated_signal.connect(self.presenceUpdateHandler)

    def presenceUpdateHandler(self):
        list_of_workstation = self.backend.getWorkstationList()

        for i, workstation in enumerate(list_of_workstation):
            self.machine_page.updateMachineStatus("machine_" + str(i), workstation['jid'], workstation['status'])
        
        pass

    def open_tab_slot(self, name, address):
        if name not in self.opened_tab_name_list:
            self.work_tab = MachineActionPage(self.backend.createWorkstationBackend(address), name, self)
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