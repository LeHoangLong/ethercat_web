from PyQt5 import QtWidgets, QtCore
from DualButtonWidget import DualButtonWidget
from NodeTree import NodeTree
from LabeledComboBox import LabeledComboBox

class AddCollectData(QtWidgets.QDialog):
    selected_data_collector_signal = QtCore.pyqtSignal(dict)
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.backend = backend
        self.node_tree = NodeTree(self.backend)
        self.node_tree.showAllNodeData()
        self.node_tree.setItemFlag(QtCore.Qt.ItemIsUserCheckable)
        self.type_list = LabeledComboBox('Collect type')
        list_of_supported_collect_type = self.backend.getSupportedCollectorType()
        for collect_type in list_of_supported_collect_type:
            self.type_list.combo_box.addItem(collect_type)
        self.ok_cancel_button = DualButtonWidget("Ok", "Cancel", direction=1)
        self.ok_cancel_button.button_1.clicked.connect(self.okButtonClickedHandler)
        self.ok_cancel_button.button_2.clicked.connect(self.cancelButtonClickedHandler)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.node_tree)
        self.main_layout.addWidget(self.type_list)
        self.main_layout.addWidget(self.ok_cancel_button)
        self.setLayout(self.main_layout)
    
    def cancelButtonClickedHandler(self):
        self.close()
    
    def okButtonClickedHandler(self):
        if self.node_tree.selected_item != None:
            data_name = ''
            data_type = ''
            itr = self.node_tree.selected_item
            while itr != None and itr != self.node_tree:
                data_name = '/' + itr.text(0) + data_name
                if itr.columnCount() > 1:
                    data_type = itr.text(1)
                itr = itr.parent()

            selected_collector_dict = {
                'data_name': data_name,
                'data_type': data_type,
                'collector_type': self.type_list.currentText()
            }
            self.selected_data_collector_signal.emit(selected_collector_dict)
        self.close()

class CollectDataSetupWidget(QtWidgets.QWidget):
    added_collector_list_updated = QtCore.pyqtSignal()

    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.collecting_data_tree_widget_header = QtWidgets.QTreeWidgetItem(["Data name", "type"])

        self.collecting_data_tree_widget = QtWidgets.QTreeWidget()
        self.collecting_data_tree_widget.setColumnCount(2)
        self.collecting_data_tree_widget.setHeaderItem(self.collecting_data_tree_widget_header) 

        self.collect_data_add_remove_button_widget = DualButtonWidget("Add", "Remove")
        self.collect_data_add_remove_button_widget.button_1.clicked.connect(self.addButtonClickHandler)

        self.collect_data_label = QtWidgets.QLabel('Collecting data')

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.collect_data_label)
        self.main_layout.addWidget(self.collecting_data_tree_widget)
        self.main_layout.addWidget(self.collect_data_add_remove_button_widget)
        self.main_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.setLayout(self.main_layout)
        self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.added_collector = []

    def addButtonClickHandler(self):
        self.collect_data_dialog = AddCollectData(self.backend, self)
        self.collect_data_dialog.selected_data_collector_signal.connect(self.dataCollectorAddSignalHandler)
        self.collect_data_dialog.show()

    def dataCollectorAddSignalHandler(self, collector_dict):
        already_added = False
        for i in self.added_collector:
            if i == collector_dict:
                already_added = True
                break
        
        if already_added == False:
            new_tree_item = QtWidgets.QTreeWidgetItem([collector_dict['data_name'], collector_dict['collector_type']])
            self.added_collector.append(collector_dict)
            self.added_collector_list_updated.emit()
            self.collecting_data_tree_widget.addTopLevelItem(new_tree_item)

    def getAddedCollector(self):
        return self.added_collector
