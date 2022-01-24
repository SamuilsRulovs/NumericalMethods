import sys
import numpy as np

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QMessageBox, QLineEdit, QPushButton, QDialog, QFormLayout
from PyQt5 import QtCore, QtWidgets

import utilities as uti
from pointSelector import myPointSelector
from polygonSelector import myPolygonSelector
from Data import Data
from computeKernel import ComputeKernel
from creatFlagMtx import createFlagMtx

matplotlib.use('qt5Agg')


def coords2Index(x, y, h):
    return int(np.round(x / h)), int(np.round(y / h))


class DimensionAndResolutionDialog(QDialog):
    accepted = QtCore.pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolution = QLineEdit("9")
        self.resolution.textEdited[str].connect(self.unlock)
        self.dimension = QLineEdit("4")
        self.dimension.textEdited[str].connect(self.unlock)
        self.btn = QPushButton('OK')
        self.btn.setDisabled(False)
        self.btn.clicked.connect(self.ok_pressed)

        form = QFormLayout(self)
        form.addRow('Resolution', self.resolution)
        form.addRow('Dimension', self.dimension)
        form.addRow(self.btn)

    def unlock(self, text):
        pass

    def ok_pressed(self):
        values = {'Resolution': self.resolution.text(),
                  'Dimension': self.dimension.text()}
        self.accepted.emit(values)
        self.accept()


class PillarHeightDialog(QDialog):
    accepted = QtCore.pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pillarHeight = QLineEdit("5")
        self.pillarHeight.textEdited[str].connect(self.unlock)
        self.btn = QPushButton('OK')
        self.btn.setDisabled(False)
        self.btn.clicked.connect(self.ok_pressed)

        form = QFormLayout(self)
        form.addRow('Height', self.pillarHeight)
        form.addRow(self.btn)

    def unlock(self, text):
        pass

    def ok_pressed(self):
        '''When use presses OK, this function will send values'''
        values = {'Height': self.pillarHeight.text()}
        self.accepted.emit(values)
        self.accept()


class MplCanvas(FigureCanvasQTAgg):
    '''Matplotlib canvas. It enables us to draw matplotlib plots on pyqt5 windows'''

    def __init__(self, resolution, dimension, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)

        self.__initilize2DAnd3DAxes(resolution, dimension)

    def __initilize2DAnd3DAxes(self, resolution, dimension):
        ## Initilize 2D plot
        self.axLeft2D = self.fig.add_subplot(1, 2, 1)
        self.h = dimension / float(resolution - 1)
        self.lengthUpperBound = dimension + self.h - 1e-15

        ## Create grid points on the plot
        grid_x = np.tile(np.arange(0, self.lengthUpperBound, self.h), resolution)
        grid_y = np.repeat(np.arange(0, self.lengthUpperBound, self.h), resolution)
        self.pts = self.axLeft2D.scatter(grid_x, grid_y)

        ## Initilize 3D plot
        self.axRight3D = self.fig.add_subplot(1, 2, 2, projection='3d')


class UserInteraction:
    '''Responsible for collecting necessary user input.'''

    def __init__(self):
        self.isCanvasSet = False
        self.resolution = int()
        self.dimension = float()
        self.pillarHeights = []
        self.pillarCoords = []

    def setCanvas(self, matPlotLibCanvas):
        self.canvas = matPlotLibCanvas
        self.isCanvasSet = True
        self.__savePointColors()

    def setData(self):
        self.data = Data(self.resolution)

    def askUserDimAndReso(self):
        inp = DimensionAndResolutionDialog()

        ## the input from the user will be saved in a dictionary(here called values) and forwarded to the __saveDimAndReso function.
        inp.accepted.connect(self.__saveDimAndReso)

        inp.exec_()

    def __saveDimAndReso(self, input_values):
        '''Once the user submits the dimension and resolution, it will be saved here'''

        self.dimension = float(input_values['Dimension'])
        self.resolution = int(input_values['Resolution'])

    def __savePillarHeights(self, input_values):
        self.pillarHeights.append(float(input_values['Height']))

    def __savePointColors(self):
        '''Saving the color value of the points on the 2D grid, so that we can change them later'''

        xys = self.canvas.pts.get_offsets()
        Npts = len(xys)
        self.fc = self.canvas.pts.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (Npts, 1))

    def connectPointSelector(self):
        '''Ask the user for the height of the Pillar and let the point selector guide the user for spacial selection'''
        inp = PillarHeightDialog()

        ## the input from the user will be saved in a dictionary(here called values) and forwarded to the __savePillarHeights function.
        inp.accepted.connect(self.__savePillarHeights)
        inp.exec_()

        self.pointSelector = myPointSelector(self.canvas.axLeft2D, self.canvas.h, self.onPillarSelect)
        print(self.pillarHeights)

    def getDimAndReso(self):
        return self.dimension, self.resolution

    def initCompute(self):
        print("Initialising computations")
        computations = ComputeKernel(self.data)
        computations.compute()
        self.data = computations.data
        self.initPostProcess(computations)

    def initPostProcess(self, computations):
        print("Initialising computations")
        mesh_x, mesh_y, mesh_z = computations.postprocess()
        self.canvas.axRight3D.plot_surface(mesh_x, mesh_y, mesh_z)

    def onPillarSelect(self, selectedPillarVertices):
        '''Selected vertices are provided from point selector object.'''
        self.pointSelector.disconnect_events()
        self.pointSelector.set_visible(False)

        self.__changeSelectedPillarColor(selectedPillarVertices)
        self.pointSelector.update()
        self.pillarCoords.append(selectedPillarVertices)
        print(f'Pillar Coords {self.pillarCoords}')

    def connectPolygonSelector(self):
        self.polygonSel = myPolygonSelector(self.canvas.axLeft2D, self.canvas.h, self.onPolygonCornersSelect)

    def onPolygonCornersSelect(self, vert):
        corners = vert
        corners.append(corners[0])
        self.data.cornerIndex = [uti.coords2Index(v[0], v[1], self.canvas.h) for v in corners]
        calculateFlagMtx = createFlagMtx(self.data)
        ## get a matrix with 2:edge, 3: corner
        calculateFlagMtx.getBorderPolygon(self.canvas.h)
        calculateFlagMtx.callFloodFill(0, 0)

    def __changeSelectedPillarColor(self, selectedPillarVertices):

        ## Get the index of the selectedPillarVertices from their spacial coordinates
        pillarIndex = [coords2Index(vert[0], vert[1], self.canvas.h) for vert in selectedPillarVertices]
        ## Making the selected vertices a bit more opaque
        self.fc[[self.resolution * yInd + xInd for xInd, yInd in pillarIndex], -1] = 0.5
        self.canvas.pts.set_facecolors(self.fc)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initilize()

    def initilize(self):
        self.interactor = UserInteraction()
        self.interactor.askUserDimAndReso()
        self.interactor.setData()

        self.dimension, self.resolution = self.interactor.getDimAndReso()

        sc = MplCanvas(self.resolution, self.dimension, self, width=5, height=4, dpi=100)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, self)

        self.interactor.setCanvas(sc)

        self.buttonLayout = QtWidgets.QHBoxLayout()

        self.pillarButton = QtWidgets.QPushButton('Add Pillar', self)
        self.calculate = QtWidgets.QPushButton('Start calculation', self)
        self.polygonInput = QtWidgets.QPushButton('Polygon Input', self)
        self.closeButton = QtWidgets.QPushButton('Close', self)
        self.restartButton = QtWidgets.QPushButton('Restart', self)

        self.pillarButton.clicked.connect(self.interactor.connectPointSelector)
        self.calculate.clicked.connect(self.interactor.initCompute)
        self.polygonInput.clicked.connect(self.interactor.connectPolygonSelector)
        self.closeButton.clicked.connect(self.close)
        self.restartButton.clicked.connect(self.restart)

        layout = QtWidgets.QGridLayout()

        layout.addWidget(toolbar, 0, 0)
        layout.addWidget(sc, 1, 0)
        layout.addWidget(self.pillarButton, 0, 1)
        layout.addWidget(self.calculate, 0, 2)
        layout.addWidget(self.polygonInput, 0, 3)
        layout.addWidget(self.closeButton, 3, 1)
        layout.addWidget(self.restartButton, 3, 2)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle('Membrane Application')

        self.show()

    def onPillarSelect(self, selectedPillarVertices):
        '''After the user presses right click, selected vertices are provided from point selector object.'''
        self.pointSelector.disconnect_events()
        self.pointSelector.set_visible(False)
        self.pointSelector.update()
        print(f"Selected pillars are {selectedPillarVertices}")

    def restart(self):
        self.close()
        self.initilize()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()
