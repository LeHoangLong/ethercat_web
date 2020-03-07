from PyQt5 import QtWidgets, QtCore, QtGui
from LabeledComboBox import LabeledComboBox
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class HistogramPlotter(QtWidgets.QWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.data_to_plot = LabeledComboBox('data')
        self.backendCollectedDataUpdated()
        self.backend.collected_data_updated_signal.connect(self.backendCollectedDataUpdated)

        self.plot, self.ax = plt.subplots()
        self.plotWidget = FigureCanvas(self.plot)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.data_to_plot)
        self.main_layout.addWidget(self.plotWidget)
        self.setLayout(self.main_layout)

        self.data_to_plot.combo_box.currentTextChanged.connect(self.dataChangedHandler)
        self.dataChangedHandler(self.data_to_plot.combo_box.currentText())

    def backendCollectedDataUpdated(self):
        self.collected_data = self.backend.getCollectedData()
        if len(self.collected_data) > 0:
            self.data_to_plot.addItems(self.collected_data[0].keys())

    def dataChangedHandler(self, text):
        data = []
        for collected_data in self.collected_data:
            data.append(collected_data[text])
        self.ax.clear()
        self.ax.hist(data, bins=10)
        self.plot.canvas.draw_idle()

