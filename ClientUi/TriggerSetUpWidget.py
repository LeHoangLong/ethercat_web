from PyQt5 import QtWidgets, QtCore
from AddDataTriggerDialog import AddDataTriggerDialog

class TriggerSetUpWidget(QtWidgets.QWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend

        #start trigger set up widget
        self.start_trigger_add_button = QtWidgets.QPushButton("Add start trigger")
        self.start_trigger_add_button.clicked.connect(self.addStartTriggerButtonClickedHandler)
        self.start_trigger_remove_button = QtWidgets.QPushButton("Remove start trigger")
        self.start_trigger_remove_button.clicked.connect(self.removeStartTriggerButtonClickedHandler)

        self.start_trigger_add_remove_button_layout = QtWidgets.QHBoxLayout()
        self.start_trigger_add_remove_button_layout.addWidget(self.start_trigger_add_button)
        self.start_trigger_add_remove_button_layout.addWidget(self.start_trigger_remove_button)
        self.start_trigger_add_remove_button_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.start_trigger_condition_list_widget = QtWidgets.QListWidget()

        self.start_trigger_label = QtWidgets.QLabel("Start trigger")


        self.start_trigger_layout = QtWidgets.QVBoxLayout()
        self.start_trigger_layout.addWidget(self.start_trigger_label)
        self.start_trigger_layout.addWidget(self.start_trigger_condition_list_widget)
        self.start_trigger_layout.addLayout(self.start_trigger_add_remove_button_layout)
        self.start_trigger_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        
        self.start_trigger_widget = QtWidgets.QWidget()
        self.start_trigger_widget.setLayout(self.start_trigger_layout)
        self.start_trigger_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        ################################################################################
        
        #end trigger set up widget
        self.end_trigger_add_button = QtWidgets.QPushButton("Add end trigger")
        self.end_trigger_add_button.clicked.connect(self.addEndTriggerButtonClickedHandler)
        
        self.end_trigger_remove_button = QtWidgets.QPushButton("Remove start trigger")
        self.end_trigger_remove_button.clicked.connect(self.removeEndTriggerButtonClickedHandler)

        self.end_trigger_add_remove_button_layout = QtWidgets.QHBoxLayout()
        self.end_trigger_add_remove_button_layout.addWidget(self.end_trigger_add_button)
        self.end_trigger_add_remove_button_layout.addWidget(self.end_trigger_remove_button)
        self.end_trigger_add_remove_button_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.end_trigger_condition_list_widget = QtWidgets.QListWidget()

        self.end_trigger_label = QtWidgets.QLabel("End trigger")

        self.end_trigger_layout = QtWidgets.QVBoxLayout()
        self.end_trigger_layout.addWidget(self.end_trigger_label)
        self.end_trigger_layout.addWidget(self.end_trigger_condition_list_widget)
        self.end_trigger_layout.addLayout(self.end_trigger_add_remove_button_layout)
        self.end_trigger_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        
        self.end_trigger_widget = QtWidgets.QWidget()
        self.end_trigger_widget.setLayout(self.end_trigger_layout)
        self.end_trigger_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        ################################################################################

        #trigger set up widget
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.start_trigger_widget)
        self.main_layout.addWidget(self.end_trigger_widget)

        self.setLayout(self.main_layout)

        self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        ################################################################################
        self.start_trigger_list = []
        self.end_trigger_list = []

    def addStartTriggerButtonClickedHandler(self):
        self.start_dialog = AddDataTriggerDialog(self.backend)
        self.start_dialog.selected_trigger_signal.connect(self.selectedStartTriggerSignalHandler)
        self.start_dialog.show()
        pass

    def removeStartTriggerButtonClickedHandler(self):
        del self.start_trigger_list[self.start_trigger_condition_list_widget.currentRow()]
        self.start_trigger_condition_list_widget.takeItem(self.start_trigger_condition_list_widget.currentRow())

    def addEndTriggerButtonClickedHandler(self):
        self.end_dialog = AddDataTriggerDialog(self.backend)
        self.end_dialog.selected_trigger_signal.connect(self.selectedEndTriggerSignalHandler)
        self.end_dialog.show()
        pass

    def removeEndTriggerButtonClickedHandler(self):
        del self.end_trigger_list[self.end_trigger_condition_list_widget.currentRow()]
        self.end_trigger_condition_list_widget.takeItem(self.end_trigger_condition_list_widget.currentRow())

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

    def selectedStartTriggerSignalHandler(self, trigger_list):
        for trigger in trigger_list:
            if trigger not in self.start_trigger_list:
                trigger_str = trigger['condition_A'] + ' '  + trigger['comparison'] + ' '  + trigger['condition_B'] 
                self.start_trigger_condition_list_widget.addItem(trigger_str)
                self.start_trigger_list.append(trigger)


    def selectedEndTriggerSignalHandler(self, trigger_list):
        for trigger in trigger_list:
            if trigger not in self.end_trigger_list:
                trigger_str = trigger['condition_A'] + ' ' + trigger['comparison'] + ' '  + trigger['condition_B'] 
                self.end_trigger_condition_list_widget.addItem(trigger_str)
                self.end_trigger_list.append(trigger)

    def getStartTrigger(self):
        return self.start_trigger_list

    def getEndTrigger(self):
        return self.end_trigger_list