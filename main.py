import sys
import time
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, QObject
from PyQt6.QtGui import QIcon, QAction
from PyQt6 import uic

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 1000)

        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)

        open_file_action = QAction("Open File", self)
        open_file_action.triggered.connect(self.open_file)

        toolbar = QtWidgets.QToolBar(self)
        toolbar.setMovable(False)
        toolbar.addAction(open_file_action)
        self.addToolBar(toolbar)

        self.layout = QtWidgets.QVBoxLayout(self._main) 

    def open_file(self):
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        dialog = QtWidgets.QFileDialog(self)
        filename = dialog.getOpenFileName()[0]

        self.X, self.Y = self.read_data(filename)
        self.A = int(self.X[0])
        self.B = int(self.X[-1])

        sliderA = QtWidgets.QSlider(Qt.Orientation.Horizontal, self)
        sliderA.setMinimum(self.A)
        sliderA.setMaximum(self.B)
        sliderA.valueChanged[int].connect(self.update_A)

        sliderB = QtWidgets.QSlider(Qt.Orientation.Horizontal, self)
        sliderB.setMinimum(self.A)
        sliderB.setMaximum(self.B)
        sliderB.setValue(self.B)
        sliderB.valueChanged[int].connect(self.update_B)

        self.layout.addWidget(sliderB)
        self.layout.addWidget(sliderA)

        self.static_canvas = FigureCanvas(Figure())
        self.layout.addWidget(NavigationToolbar(self.static_canvas, self))
        self.layout.addWidget(self.static_canvas)

        (self.ax1, self.ax2) = self.static_canvas.figure.subplots(2, 1)

        self.update_canvas(self.A, self.B)
    
    def update_A(self, A):
        if (A < self.B):
            self.update_canvas(A, self.B)

    def update_B(self, B):
        if (self.A < B):
            self.update_canvas(self.A, B)

    def update_canvas(self, A, B):
        self.A = A
        self.B = B

        X, Y = self.filter_XY(self.X, self.Y, A, B)
        a, b = self.calculate(X, Y)

        t1 = np.array(X)
        t2 = np.array(X)

        def f(x):
            return a * x + b

        def f2(x):
            return Y - f(x)
    
        self.ax1.cla()
        self.ax1.title.set_text("Approximation")
        self.ax1.plot(X, Y, 'bo', t1, f(t1), 'k')
        self.ax1.grid(True)

        self.ax2.cla()
        self.ax2.title.set_text("Deviation")
        self.ax2.plot(t2, f2(t2), 'ro')
        self.ax2.hlines(y = 0, xmin = A, xmax = B, color='black')
        self.ax2.axis((A, B, -10, 10))
        self.ax2.grid(True)

        self.static_canvas.figure.subplots_adjust(hspace=0.3)
        self.static_canvas.figure.canvas.draw_idle()

    def read_data(self, path):
        file = open(path, 'r')

        l = 0
        X = []
        Y = []
        for line in file.readlines():
            if l > 6:
                row = line.split()
                X.append(float(row[0]))
                Y.append(float(row[4]))
            l += 1

        Y = np.rad2deg(np.unwrap(np.deg2rad(Y)))

        return X, Y
    
    def calculate(self, X, Y):
        n = len(X)
        m1 = 0
        for i in range(n):
            m1 += X[i] * Y[i]

        a = (n * m1 - sum(X) * sum(Y)) / ((n * sum(map(lambda x: x**2, X))) - (sum(X))**2)
        b = (sum(Y) - a * sum(X)) / n

        return a, b
    
    def filter_XY(self, X, Y, A, B):
        new_X = []
        new_Y = []

        for i in range(len(X)):
            if A <= X[i] <= B:
                new_X.append(X[i])
                new_Y.append(Y[i])

        return new_X, new_Y
    

if __name__ == "__main__":
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.setWindowTitle("Phase Deviation Tool")
    app.setWindowIcon(QIcon("ui/favicon.png"))
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()