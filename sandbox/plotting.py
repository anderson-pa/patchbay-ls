from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt
import time
from PySide2.QtWidgets import QVBoxLayout, QFrame, QFileDialog
import numpy as np
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class Patch:
    def __init__(self, parent):
        self._parent = parent
        self.widgets = {}
        self.series = None

        self.ui = self.make_ui()

        # self._timer = self.dynamic_canvas.new_timer(100,
        #                                             [(self._update_canvas,
        #                                               (), {})])
        # self._timer.
        # self.dynamic_canvas.mpl_connect('close_event', lambda *a: self._timer.stop())

    def make_ui(self):
        self.q_chart = QtCharts.QChart()
        self.q_chart.legend().hide()

        self.q_chart.createDefaultAxes()

        # Setting X-axis
        self.axis_x = QtCharts.QValueAxis()
        # self.axis_x.setTickCount(10)
        # self.axis_x.setTitleText("sample")
        self.q_chart.addAxis(self.axis_x, Qt.AlignBottom)

        # Setting Y-axis
        self.axis_y = QtCharts.QValueAxis()
        # self.axis_y.setTickCount(10)
        # self.axis_y.setLabelFormat("%.2f")
        # self.axis_y.setTitleText("V")
        self.q_chart.addAxis(self.axis_y, Qt.AlignLeft)

        self.plot_series("Magnitude (Column 1)", [(0, 1), (2, 2)], True)

        chart_view = QtCharts.QChartView(self.q_chart)
        # chart_view.setRenderHint(QPainter.Antialiasing)

        self.widgets['chart'] = chart_view

        # matplotlib plot
        # https://matplotlib.org/gallery/user_interfaces/embedding_in_qt_sgskip.html
        static_canvas = FigureCanvas(Figure(tight_layout=True))
        static_toolbar = NavigationToolbar(static_canvas, self._parent)
        static_toolbar.setObjectName('StaticToolBar')
        # self._parent.addToolBar(Qt.TopToolBarArea, static_toolbar)

        self.dynamic_canvas = FigureCanvas(Figure(tight_layout=True))

        self._parent.addToolBar(Qt.BottomToolBarArea,
                                NavigationToolbar(self.dynamic_canvas, self._parent))

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")
        self._static_ax.grid()

        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self._dynamic_ax.tick_params(labelsize=20)
        self._dynamic_ax.set_xlabel('hello')

        # self._dynamic_ax.set_autoscale_on(True)
        # self._dynamic_ax.autoscale_view(True, True, True)

        # t = np.linspace(0, 10, 1)
        # y = np.sin(t + time.time())
        # Shift the sinusoid as a function of time.
        self.dynamic_line, = self._dynamic_ax.plot([], [], 'r.')
        # self._dynamic_ax.xaxis.set_label_size(2)

        vbox = QVBoxLayout()
        vbox.addWidget(chart_view)
        vbox.addWidget(static_canvas)
        vbox.addWidget(static_toolbar)
        vbox.addWidget(self.dynamic_canvas)

        main_widget = QFrame()
        main_widget.setLayout(vbox)

        return main_widget

    def run(self):
        # self.plot_series('series2',  [(1, 1.5), (2, 3), (4, 5)], False)
        # self.axis_x.setRange(0, 40)
        # self.axis_y.setRange(-1, 2)
        # self._timer.start()
        # self._update_canvas()
        self.update_no_clear()
        QFileDialog.getSaveFileName(self._parent, "Choose something",
                                    '/home/phillip/test.png', ';;',
                                    options=QFileDialog.DontUseNativeDialog)

    def close(self):
        # self._timer.stop()
        # del self._timer
        pass

    def plot_series(self, name, data, new):
        # Create QLineSeries
        if self.series is None:
            self.series = QtCharts.QScatterSeries()
        self.series.setName(name)

        # Filling QLineSeries
        for p in data:
            self.series.append(*p)

        if new:
            self.q_chart.addSeries(self.series)
            self.series.attachAxis(self.axis_x)
            self.series.attachAxis(self.axis_y)

        # Getting the color from the QChart to use it on the QTableView
        # self.model.color = "{}".format(self.series.pen().color().name())

    def _update_canvas(self):
        self._dynamic_ax.clear()
        self._dynamic_ax.set_xlabel('hello', {'fontsize': 20})
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        self._dynamic_ax.plot(t, np.sin(t + time.time() + np.pi/2))
        self._dynamic_ax.set_ylabel('world', {'fontsize': 20})

        self._dynamic_ax.figure.canvas.draw()

    def update_no_clear(self):
        print(self._dynamic_ax.xaxis.get_data_interval())
        t = np.linspace(0, 10, 101)
        y = np.sin(t + time.time())
        # Shift the sinusoid as a function of time.
        self.dynamic_line.set_data(t, y)
        self._dynamic_ax.relim()
        # self._dynamic_ax.autoscale_view(False, True, True)
        # self.dynamic_line.set_ydata(y)

        # self._dynamic_ax.set_xlim(0, 10)
        # self._dynamic_ax.set_ylim(-1, 1)
        # self._dynamic_ax.autoscale(True, axis='both', tight=True)
        self._dynamic_ax.autoscale()
        # self._dynamic_ax.margin(0.05)

        self.dynamic_canvas.draw()
        # self.dynamic_canvas.flush_events()

        print(self._dynamic_ax.xaxis.get_data_interval())

