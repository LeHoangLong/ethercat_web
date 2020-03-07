from PyQt5 import QtWidgets, QtCore
from LabeledComboBox import LabeledComboBox
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ScatterPlotter(QtWidgets.QWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend

        self.x_axis = LabeledComboBox('x_axis')
        self.x_axis.combo_box.currentTextChanged.connect(self.xAxisChangedHandler)
        
        self.y_axis = LabeledComboBox('y_axis')
        self.y_axis.combo_box.currentTextChanged.connect(self.yAxisChangedHandler)

        self.plot, self.ax = plt.subplots()
        self.plotWidget = FigureCanvas(self.plot)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.x_axis)
        self.main_layout.addWidget(self.y_axis)
        self.main_layout.addWidget(self.plotWidget)
        self.setLayout(self.main_layout)

        self.x_axis_data = []
        self.y_axis_data = []

        self.backendCollectedDataUpdated()
        self.backend.collected_data_updated_signal.connect(self.backendCollectedDataUpdated)
        
        self.xAxisChangedHandler(self.x_axis.combo_box.currentText())
        self.yAxisChangedHandler(self.y_axis.combo_box.currentText())

    def backendCollectedDataUpdated(self):
        self.collected_data = self.backend.getCollectedData()
        if len(self.collected_data) > 0:
            self.x_axis.addItems(self.collected_data[0].keys())
            self.y_axis.addItems(self.collected_data[0].keys())

    def xAxisChangedHandler(self, text):
        self.x_axis_data = []
        for collected_data in self.collected_data:
            self.x_axis_data.append(collected_data[text])
        self.redraw()

    def yAxisChangedHandler(self, text):
        self.y_axis_data = []
        for collected_data in self.collected_data:
            self.y_axis_data.append(collected_data[text])
        self.redraw()

    def redraw(self):
        if len(self.x_axis_data) != 0 and len(self.x_axis_data) == len(self.y_axis_data):
            self.ax.clear()
            self.ax.scatter(self.x_axis_data, self.y_axis_data)
            self.plot.canvas.draw_idle()
            pass


