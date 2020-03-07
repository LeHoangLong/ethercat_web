from PyQt5 import QtWidgets, QtCore
from LabeledComboBox import LabeledComboBox
from HistogramPlotter import HistogramPlotter
from ScatterPlotter import ScatterPlotter

class PlotPage(QtWidgets.QWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.plot_type_widget = LabeledComboBox('Plot type', self)
        self.plotter = QtWidgets.QWidget()
        suppported_plot_types = self.backend.getAvailablePlotType()
        self.plot_type_widget.addItems(suppported_plot_types)
        self.plot_type_widget.combo_box.currentTextChanged.connect(self.plotTypeTextChangeHandler)
        
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.plot_type_widget, stretch=1)
        self.main_layout.addWidget(self.plotter, stretch=20)
        
        self.setLayout(self.main_layout)
        self.plotTypeTextChangeHandler(self.plot_type_widget.combo_box.currentText())

    def plotTypeTextChangeHandler(self, text):
        plotter = None
        if text == 'HISTOGRAM':
            plotter = HistogramPlotter(self.backend, self)
        else:
            plotter = ScatterPlotter(self.backend, self)
        
        if plotter != None:
            self.plotter.setParent(None)
            self.main_layout.removeWidget(self.plotter)
            self.plotter = plotter
            self.main_layout.addWidget(self.plotter, stretch=20)