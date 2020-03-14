from PyQt5 import QtCore, QtGui, QtWidgets
from AddDataTriggerDialog import AddDataTriggerDialog
from TriggerSetUpWidget import TriggerSetUpWidget
from DualButtonWidget import DualButtonWidget
from CollectDataSetupWidget import CollectDataSetupWidget
from SelectPath import SelectPath
from Trigger import Trigger
import json

class CollectPage(QtWidgets.QWidget):
    class GenericCollectPage(QtWidgets.QWidget):
        def __init__(self, node_name, backend, parent=None):
            super().__init__(parent)
            self.backend = backend
            self.node_name = node_name

            
            #save folder widget
            try:
                metadata_file = open("meta.txt", "r")
                json_data_str =  metadata_file.read()
                json_data = json.loads(json_data_str)
                if self.parent().parent().name in json_data:
                    self.save_location_path = json_data[self.parent().parent().name]['save_location']
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
                self.parent().parent().name: {
                    "save_location": self.save_location_path,
                    "data_collect_list": self.pending_data
                }
            }
            
            meta_data_file.write(json.dumps(json_data))
            meta_data_file.close()

            for data_name, data_info in self.pending_data.items():
                self.backend.addDataCollector(data_name, data_info['collect_type'], data_info['data_type'])
            self.pending_data = {}
            self.backend.setSaveLocation(self.save_location_path)

        def startClickedHandler(self):
            self.is_collecting = not self.is_collecting

            if self.is_collecting:
                self.backend.enableDataCollection()
                self.start_button.setText("Stop")
            else:
                self.backend.disableDataCollection()
                self.start_button.setText("Start")

        def addDataCollectorButtonClickedHandler(self):
            self.dialog = self.AddDataCollectorDialog(self.backend)
            self.dialog.add_data_signal.connect(self.availableCollectDataAddHandler)
            self.dialog.setModal(True)
            self.dialog.show()


            
    class EthercatCollectPage(QtWidgets.QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.main_layout = QtWidgets.QVBoxLayout()
            self.setStyleSheet('background-color: blue')

    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.trigger_setup_widget = TriggerSetUpWidget(self.backend, self)
        self.is_collecting = False

        try:
            metadata_file = open("meta.txt", "r")
            json_data_str =  metadata_file.read()
            json_data = json.loads(json_data_str)
            if self.parent().parent().name in json_data:
                self.save_folder = json_data[self.parent().parent().name]['save_location']
            else:
                self.save_folder = ""
        except Exception:
            self.save_folder = ""

        self.save_folder = ''
        self.select_save_folder_widget = SelectPath('Select folder', self.save_folder)
        
        self.apply_button = QtWidgets.QPushButton("Apply")
        self.apply_button.clicked.connect(self.applyClickedHandler)

        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.clicked.connect(self.startClickedHandler)

        self.panel_layout = QtWidgets.QVBoxLayout()
        self.panel_layout.addWidget(self.trigger_setup_widget)
        self.panel_layout.addWidget(self.select_save_folder_widget)
        self.panel_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.panel_widget = QtWidgets.QWidget()
        self.panel_widget.setLayout(self.panel_layout)
        self.panel_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.collect_data_widget = CollectDataSetupWidget(self.backend)
        #self.view_as_label = QtWidgets.QLabel("View as")
        #self.view_as_combo_box = QtWidgets.QComboBox()
        #self.view_as_layout = QtWidgets.QHBoxLayout()
        #self.view_as_layout.addWidget(self.view_as_label, stretch=1)
        #self.view_as_layout.addWidget(self.view_as_combo_box, stretch=15)
        #self.view_as_widget = QtWidgets.QWidget(self)
        #self.view_as_widget.setLayout(self.view_as_layout)
        #self.main_layout.addWidget(self.view_as_widget, alignment=QtCore.Qt.AlignTop, stretch=1)
        #self.current_item = None
        #self.view_as_combo_box.currentTextChanged.connect(self.typeViewSelectHandler)
        #self.main_widget = QtWidgets.QDialog(self)

        self.workspace_layout = QtWidgets.QHBoxLayout()
        self.workspace_layout.addWidget(self.panel_widget)
        self.workspace_layout.addWidget(self.collect_data_widget)
        self.workspace_layout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.workspace_widget = QtWidgets.QWidget()
        self.workspace_widget.setLayout(self.workspace_layout)
        self.workspace_widget.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.workspace_widget)
        self.main_layout.addWidget(self.apply_button)
        self.main_layout.addWidget(self.start_button)

        self.setLayout(self.main_layout)

    def itemSelectHandler(self, item, column):
        if item.text(column) != self.current_item:
            type_list = self.parent().type_dict[item.text(0)]
            
            self.view_as_combo_box.clear()
            self.current_node_name = item.text(0)
            
            first_type = type_list[0]
            self.typeViewSelectHandler(first_type)

            for type_element in type_list:
                self.view_as_combo_box.addItem(type_element)


    
    def typeViewSelectHandler(self, current_type):
        #self.main_layout.removeWidget(self.main_widget)
        #self.main_widget.setParent(None)
        #del self.main_widget
        #if current_type == 'GENERIC':
        #    self.main_widget = self.GenericCollectPage(self.current_node_name, self.backend, self)
        #else:
        #    self.main_widget = self.EthercatCollectPage()
        #self.main_layout.addWidget(self.main_widget, stretch=20)
        pass


    def applyClickedHandler(self):
        meta_data_file = open("meta.txt", "w")
        self.save_folder = self.select_save_folder_widget.getSelectedPath()
        json_data = {
            self.parent().parent().name: {
                "save_location": self.select_save_folder_widget.getSelectedPath(),
                #"data_collect_list": self.pending_data
            }
        }
        
        meta_data_file.write(json.dumps(json_data))
        meta_data_file.close()

        #for data_name, data_info in self.pending_data.items():
        #    self.backend.addDataCollector(data_name, data_info['collect_type'], data_info['data_type'])
        self.pending_data = {}
        self.backend.setSaveLocation(self.save_folder)

        self.backend.clearTrigger('START_TRIGGER')
        for trigger_info in self.trigger_setup_widget.getStartTrigger():
            self.backend.addTrigger(trigger_info, 'START_TRIGGER')

        
        self.backend.clearTrigger('END_TRIGGER')
        for trigger_info in self.trigger_setup_widget.getEndTrigger():
            self.backend.addTrigger(trigger_info, 'END_TRIGGER')

        added_collector = self.collect_data_widget.getAddedCollector()
        self.backend.setCollector(added_collector)

    def startClickedHandler(self):
        self.is_collecting = not self.is_collecting

        if self.is_collecting:
            self.backend.enableDataCollection()
            self.start_button.setText("Stop")
        else:
            self.backend.disableDataCollection()
            self.start_button.setText("Start")


