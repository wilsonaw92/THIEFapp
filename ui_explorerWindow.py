from PyQt4 import QtGui, QtCore

import resources_rc

class Ui_ExplorerWindow(object):
    def setupUi(self, window):
        window.setWindowTitle("THiEF Explorer")

        self.centralWidget = QtGui.QWidget(window)
        self.centralWidget.setMinimumSize(800, 400)
        window.setCentralWidget(self.centralWidget)

        self.menubar = window.menuBar()
        self.fileMenu = self.menubar.addMenu("File")
        self.viewMenu = self.menubar.addMenu("View")
        self.modeMenu = self.menubar.addMenu("Mode")

        self.toolBar = QtGui.QToolBar(window)
        window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.actionQuit = QtGui.QAction("Quit", window)
        self.actionQuit.setShortcut(QtGui.QKeySequence.Quit)

        self.actionShowBasemapLayer = QtGui.QAction("OpenStreetMap (Online)", window)
        self.actionShowBasemapLayer.setShortcut("Ctrl+B")
        self.actionShowBasemapLayer.setCheckable(True)

        self.actionShowCountriesLayer = QtGui.QAction("Basemap (Offline)", window)
        self.actionShowCountriesLayer.setShortcut("Ctrl+C")
        self.actionShowCountriesLayer.setCheckable(True)

        self.actionShowThiefLayer = QtGui.QAction("THiEF", window)
        self.actionShowThiefLayer.setShortcut("Ctrl+T")
        self.actionShowThiefLayer.setCheckable(True)

        self.actionShowLobLayer = QtGui.QAction("LOBs", window)
        self.actionShowLobLayer.setShortcut("Ctrl+L")
        self.actionShowLobLayer.setCheckable(True)

        icon = QtGui.QIcon(":/icons/mActionZoomIn.png")
        self.actionZoomIn = QtGui.QAction(icon, "Zoom In", window)
        self.actionZoomIn.setShortcut(QtGui.QKeySequence.ZoomIn)

        icon = QtGui.QIcon(":/icons/mActionZoomOut.png")
        self.actionZoomOut = QtGui.QAction(icon, "Zoom Out", window)
        self.actionZoomOut.setShortcut(QtGui.QKeySequence.ZoomOut)

        icon = QtGui.QIcon(":/icons/mActionPan.png")
        self.actionPan = QtGui.QAction(icon, "Pan", window)
        self.actionPan.setShortcut("Ctrl+1")
        self.actionPan.setCheckable(True)

        icon = QtGui.QIcon(":/icons/mActionThief.png")
        self.actionExplore = QtGui.QAction(icon, "Zoom To THiEF", window)
        self.actionExplore.setShortcut("Ctrl+2")

        self.fileMenu.addAction(self.actionQuit)

        self.viewMenu.addAction(self.actionShowBasemapLayer)
        self.viewMenu.addAction(self.actionShowCountriesLayer)
        self.viewMenu.addAction(self.actionShowThiefLayer)
        self.viewMenu.addAction(self.actionShowLobLayer)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.actionZoomIn)
        self.viewMenu.addAction(self.actionZoomOut)

        self.modeMenu.addAction(self.actionPan)
        self.modeMenu.addAction(self.actionExplore)

        self.toolBar.addAction(self.actionZoomIn)
        self.toolBar.addAction(self.actionZoomOut)
        self.toolBar.addAction(self.actionPan)
        self.toolBar.addAction(self.actionExplore)

        window.resize(window.sizeHint())
