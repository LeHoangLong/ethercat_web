from PyQt5 import QtCore, QtGui, QtWidgets

class NodeTree(QtWidgets.QTreeWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.backend.all_node_received_signal.connect(self.listOfNodeUpdatedHandler)

        self.setColumnCount(2)
        self.node_tree_header = QtWidgets.QTreeWidgetItem(['Node data', 'Data type'])
        self.setHeaderItem(self.node_tree_header)
        self.is_node_data_shown = False
        self.flag = None
        self.added_node_name_dict = {}
        #self.itemActivated.connect(self.collect_page.itemSelectHandler)
        self.backend.getAllNodes() #backend will send request for all nodes and a signal will be emitted when the list of node is received
        self.itemClicked.connect(self.itemClickedHandler)
        self.selected_item = None
        self.selected_type = None
    
    def itemClickedHandler(self, item, column):
        for i in range(self.topLevelItemCount()):
            self.clearCheckState(self.topLevelItem(i))
        if item.childCount() == 0:
            item.setCheckState(0, QtCore.Qt.Checked)
            self.selected_item = item
            self.selected_type = item.text(1)
        
    def clearCheckState(self, tree_widget_item):
        if tree_widget_item.childCount() > 0:
            for i in range(tree_widget_item.childCount()):
                self.clearCheckState(tree_widget_item.child(i))
        else:
            tree_widget_item.setCheckState(0, QtCore.Qt.Unchecked)

    def listOfNodeUpdatedHandler(self, list_of_nodes):
        self.list_of_nodes = list_of_nodes

        for node in self.list_of_nodes:
            if node not in self.added_node_name_dict:
                node_tree_item = QtWidgets.QTreeWidgetItem(self, [node])
                self.addTopLevelItem(node_tree_item)
                self.added_node_name_dict[node] = node_tree_item
                if self.is_node_data_shown:
                    self.__showNodeData(node)


    def getSelectedNodeName(self):
        current_item = self.selected_item
        
        if current_item != None:
            while current_item.parent != self: 
                current_item = current_item.parent

        return current_item

    def getSelectedDataName(self):
        current_item = self.selected_item
        full_data_name = ''
        
        if current_item != None:
            while current_item != None and current_item != self: 
                full_data_name = '/' + current_item.text(0) + full_data_name
                current_item = current_item.parent()

        return full_data_name

    def getSelectedDataType(self):
        return self.selected_type


    def setItemFlag(self, flag):
        self.flag = flag

    def showAllNodeData(self):
        self.is_node_data_shown = True
        for node in self.added_node_name_dict: 
            self.__showNodeData(node)

    def __showNodeData(self, node):
        available_data__info_tree_list = self.backend.getAvailableCollectData(node)
        for available_data__info_tree in available_data__info_tree_list:
            self.__appendDataNode(self.added_node_name_dict[node], available_data__info_tree)

    def __appendDataNode(self, parent_node, child_info):
        child_widget = QtWidgets.QTreeWidgetItem(parent_node)
        child_widget.setText(0, child_info['name'])
        if child_info['type'] == 'list':
            grandchild_list = child_info['data']
            for grandchild_info in grandchild_list:
                self.__appendDataNode(child_widget, grandchild_info)
        else:
            child_widget.setText(1, child_info['type'])
            if self.flag != None:
                child_widget.setFlags(child_widget.flags() | self.flag)
                child_widget.setCheckState(0, QtCore.Qt.Unchecked)

