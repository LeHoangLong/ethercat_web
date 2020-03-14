from PyQt5 import QtCore, QtGui, QtWidgets
from NodeTree import NodeTree

class AddDataTriggerDialog(QtWidgets.QDialog):
    selected_trigger_signal = QtCore.pyqtSignal(list)
    class TreeWidgetItemWrapper(QtWidgets.QTreeWidgetItem):
        def __init__(self, obj=None, callback=None, parent=None):
            super().__init__(parent)
            self.my_callback_obj = obj
            self.my_callback_func = callback
            pass

    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.setModal(True)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)


        self.condition_A_header = QtWidgets.QTreeWidgetItem(['Available data'])
        #self.condition_A = QtWidgets.QTreeWidget()
        self.condition_A = NodeTree(self.backend)
        self.condition_A.setItemFlag(QtCore.Qt.ItemIsUserCheckable)
        self.condition_A.showAllNodeData()
        self.condition_A.setHeaderItem(self.condition_A_header)
        self.condition_A.itemClicked.connect(self.conditionATreeChangedHandler)
        self.condition_A.itemDoubleClicked.connect(self.conditionATreeDoubleClickedHandler)

        self.condition_B_header = QtWidgets.QTreeWidgetItem(['Available data'])
        #self.condition_B = QtWidgets.QTreeWidget()
        self.condition_B = NodeTree(self.backend)
        self.condition_B.setItemFlag(QtCore.Qt.ItemIsUserCheckable)
        self.condition_B.showAllNodeData()
        self.condition_B.setHeaderItem(self.condition_B_header)
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

        self.const_B = 0
        self.condition_B_item_list = []
        self.addNodetoConditionTree(self.condition_B, num_of_sample_node, self.condition_B_item_list)
        self.addNodetoConditionTree(self.condition_B, constant_node, self.condition_B_item_list, self.constantClickedHandler, self.const_B)
        self.selected_B = None

        self.ok_button = QtWidgets.QPushButton('OK')
        self.ok_button.clicked.connect(self.okButtonClickedHandler)

        self.ok_button_layout = QtWidgets.QVBoxLayout()
        self.ok_button_layout.addWidget(self.ok_button)
        self.ok_button_layout.addStretch(1)
        self.ok_button_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        
        self.ok_button_widget = QtWidgets.QWidget()
        self.ok_button_widget.setLayout(self.ok_button_layout)
        self.ok_button_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.main_layout.addWidget(self.condition_A)
        self.main_layout.addWidget(self.comparison_widget)
        self.main_layout.addWidget(self.condition_B)
        self.main_layout.addWidget(self.ok_button_widget)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)

    def okButtonClickedHandler(self):
        if self.selected_A != None and self.selected_B != None:
            condition_A_name = self.condition_A.getSelectedDataName()
            condition_A_type = self.condition_A.getSelectedDataType()
            condition_B_name = self.condition_B.getSelectedDataName()
            condition_B_type = self.condition_B.getSelectedDataType()

            trigger_list = [
                {
                    'condition_A': condition_A_name,
                    'condition_A_type': condition_A_type,
                    'condition_B': condition_B_name,
                    'condition_B_type': condition_B_type,
                    'comparison': self.comparison_box.currentText()
                }
            ]
            self.selected_trigger_signal.emit(trigger_list)
            #self.backend.addTrigger(self.selected_A.text(0), self.selected_B.text(0), self.comparison_box.currentText(), self.name)
        self.close()

    def conditionATreeChangedHandler(self, item, column):
        if item.childCount() == 0:
            #self.clearCheckState(self.condition_A_item_list)
            #item.setCheckState(0, QtCore.Qt.Checked)
            self.selected_A = item

    def conditionBTreeChangedHandler(self, item, column):
        if item.childCount() == 0:
            #self.clearCheckState(self.condition_B_item_list)
            #item.setCheckState(0, QtCore.Qt.Checked)
            self.selected_B = item

    def conditionATreeDoubleClickedHandler(self, item, column):
        if isinstance(item, self.TreeWidgetItemWrapper) and item.my_callback_func != None:
            item.my_callback_func(item, item.my_callback_obj, 'DOUBLE_CLICKED')

    def conditionBTreeDoubleClickedHandler(self, item, column):
        if isinstance(item, self.TreeWidgetItemWrapper) and item.my_callback_func != None:
            item.my_callback_func(item, item.my_callback_obj, 'DOUBLE_CLICKED')

    def constantClickedHandler(self, item, my_callback_obj, callback_type):
        if callback_type == 'DOUBLE_CLICKED':
            value, ok = QtWidgets.QInputDialog.getDouble(self, 'Constant value', 'Enter number')
            if ok:
                item.setText(0, 'Constant: ' + str(value))

    def clearCheckState(self, item_list):
        for item in item_list:
            if item.childCount() == 0:
                item.setCheckState(0, QtCore.Qt.Unchecked)

    def addNodetoConditionTree(self, tree, node, condition_item_list, callback=None, my_callback_obj=None):
        #child = QtWidgets.QTreeWidgetItem(tree)
        child = self.TreeWidgetItemWrapper(my_callback_obj, callback, tree)
        child.setText(0, node['name'])
        if node['type'] == 'list':
            node_list = node['data']
            for node in node_list:
                self.addNodetoConditionTree(child, node, condition_item_list)
        else:
            child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
            child.setCheckState(0, QtCore.Qt.Unchecked)

        condition_item_list.append(child)
