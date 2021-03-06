# pydebug below
# import pdb
import os, os.path, sys
import math
import csv
import shapefile
import qgis.utils
from qgis.core import *
from qgis.gui import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ui_explorerWindow import Ui_ExplorerWindow

import resources_rc


# pydebug
# pdb.set_trace()

# SETUP GUI
class MapExplorer(QMainWindow, Ui_ExplorerWindow):

    # CACHE VARIABLES FOR csvThiefRefresh FUNCTION
    lastX = 0.
    lastY = 0.

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.connect(self.actionQuit,
                     SIGNAL("triggered()"), qApp.quit)
        self.connect(self.actionShowThiefLayer,
                     SIGNAL("triggered()"), self.showThiefLayer)

        self.connect(self.actionShowCountriesLayer,
                     SIGNAL("triggered()"), self.showCountriesLayer)

        self.connect(self.actionShowLobLayer,
                     SIGNAL("triggered()"), self.showLobLayer)
        self.connect(self.actionShowBasemapLayer,
                     SIGNAL("triggered()"), self.showBasemapLayer)
        self.connect(self.actionZoomIn,
                     SIGNAL("triggered()"), self.zoomIn)
        self.connect(self.actionZoomOut,
                     SIGNAL("triggered()"), self.zoomOut)
        self.connect(self.actionPan,
                     SIGNAL("triggered()"), self.setPanMode)
        self.connect(self.actionExplore,
                     SIGNAL("triggered()"), self.setExploreMode)


        # SET MAP CANVAS PARAMETERS
        self.mapCanvas = QgsMapCanvas()
        self.mapCanvas.useImageToRender(True)
        self.mapCanvas.enableAntiAliasing(True)
        self.mapCanvas.setCanvasColor(Qt.white)
        self.mapCanvas.setCrsTransformEnabled(True)
        self.mapCanvas.setDestinationCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
        self.mapCanvas.show()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mapCanvas)
        self.centralWidget.setLayout(layout)

        self.actionShowBasemapLayer.setChecked(True)
        self.actionShowThiefLayer.setChecked(True)
        self.actionShowCountriesLayer.setChecked(True)
        self.actionShowLobLayer.setChecked(True)

        self.panTool = PanTool(self.mapCanvas)
        self.panTool.setAction(self.actionPan)

        # CREATE LEGEND
        self.root = QgsProject.instance().layerTreeRoot()
        self.bridge = QgsLayerTreeMapCanvasBridge(self.root, self.mapCanvas)
        self.model = QgsLayerTreeModel(self.root)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.model.setFlag(QgsLayerTreeModel.ShowLegend)
        self.view = QgsLayerTreeView()
        self.view.setModel(self.model)

        self.LegendDock = QDockWidget("Layers", self)
        self.LegendDock.setObjectName("layers")
        self.LegendDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.LegendDock.setWidget(self.view)
        self.LegendDock.setContentsMargins(9, 9, 9, 9)
        self.LegendDock.setMinimumWidth(200)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.LegendDock)

        cur_dir = os.path.dirname(os.path.realpath(__file__)) #SET RELATIVE PATHS


        # WATCH FOR CHANGES IN RELEVANT FILES
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(os.path.join(cur_dir, "data", "test.csv"))
        self.watcher.fileChanged.connect(self.csvLobRefresh)
        self.watcher.fileChanged.connect(self.csvThiefRefresh)

        # OPENSTREETMAP SCALES FOR zoomToScale FUNCTION
        self.predefinedScales = [
                591657528,
                295828764,
                147914382,
                73957191,
                36978595,
                18489298,
                9244649,
                4622324,
                2311162,
                1155581,
                577791,
                288895,
                144448,
                72224,
                36112,
                18056,
                9028,
                4514,
                2257,
                1128,
                564,
                282,
                141,
                71
            ]

        self.mapCanvas.scaleChanged.connect(self.zoomToScale)

    # LOAD MAP LAYERS TO GUI
    def loadMap(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        layers = []

        filename = os.path.join(cur_dir, "data", "WORLDMAPWebMerc.tif")
        self.countries_layer = QgsRasterLayer(filename, "Basemap (Offline)")
        QgsMapLayerRegistry.instance().addMapLayer(self.countries_layer)
        layers.append(QgsMapCanvasLayer(self.countries_layer))

        filename = os.path.join(cur_dir, "data", "openstreetmap.xml")
        self.basemap_layer = QgsRasterLayer(filename, "OSM Webmap")
        QgsMapLayerRegistry.instance().addMapLayer(self.basemap_layer)
        layers.append(QgsMapCanvasLayer(self.basemap_layer))

        filename = os.path.join(cur_dir, "data", "line_points.shp")
        self.loblayer = QgsVectorLayer(filename, "LOBs", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.loblayer)
        layers.append(QgsMapCanvasLayer(self.loblayer))

        filename = os.path.join(cur_dir, "data", "thiefsymbolcsvshp.shp")
        self.thieflayer = QgsVectorLayer(filename, "THiEF", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(self.thieflayer)
        layers.append(QgsMapCanvasLayer(self.thieflayer))

        layers.reverse()
        self.showVisibleMapLayers()
        self.mapCanvas.setLayerSet(layers)
        self.mapCanvas.setExtent(self.loblayer.extent())

        # SET LABEL RULES
        self.thieflayer.setCustomProperty("labeling", "pal")
        self.thieflayer.setCustomProperty("labeling/isExpression", True)
        self.thieflayer.setCustomProperty("labeling/enabled", True)
        self.thieflayer.setCustomProperty("labeling/bufferDraw", True)
        self.thieflayer.setCustomProperty("labeling/bufferSize", "1")
        self.thieflayer.setCustomProperty("labeling/bufferColor", "white")
        self.thieflayer.setCustomProperty("labeling/fontFamily", "Arial")
        self.thieflayer.setCustomProperty("labeling/textTransp", "30")
        self.thieflayer.setCustomProperty("labeling/bufferTransp", "30")
        self.thieflayer.setCustomProperty("labeling/fontSize", "8")
        self.thieflayer.setCustomProperty("labeling/fieldName",
                                          "'Az: '  || AZIMUTH || '\n' || 'X: ' ||  X ||  '\n'  || 'Y: '  ||   Y")
        self.thieflayer.setCustomProperty("labeling/placement", "3")
        self.thieflayer.setCustomProperty("labeling/dist", "5")

    # SET ZOOM LEVELS TO OPENSTREETMAP SCALES
    def zoomToScale(self):
        self.mapCanvas.scaleChanged.disconnect(self.zoomToScale)
        scale = self.mapCanvas.scale()
        targetScale = min(self.predefinedScales, key=lambda x: abs(x - scale))
        self.mapCanvas.zoomScale(targetScale)
        self.mapCanvas.scaleChanged.connect(self.zoomToScale)



    # DEFINE POINT/LINE SYMBOLOGY
    def setSymbology(self):
        print "setsymbology"
        my_rules = {
            'LOB': ('#FF3333', .7, 'LOB'),
            'DF': ('#3333FF', 2, 'DF'),
        }

        categories = []
        for lob, (color, width, label) in my_rules.items():
            self.sym = QgsSymbolV2.defaultSymbol(self.loblayer.geometryType())
            self.sym.setColor(QColor(color))
            self.sym.setWidth(width)
            self.sym.setOutputUnit(QgsSymbolV2.MM)
            category = QgsRendererCategoryV2(lob, self.sym, label)
            categories.append(category)

        renderer = QgsCategorizedSymbolRendererV2('ID', categories)
        self.loblayer.setRendererV2(renderer)


        symbol = QgsMarkerSymbolV2.createSimple({})
        symbol.deleteSymbolLayer(0)
        cur_dir = os.path.dirname(os.path.realpath(__file__))

        symbol_layer = QgsSvgMarkerSymbolLayerV2()
        symbol_layer.setPath(os.path.join(cur_dir, "data", "thiefarrow.svg"))
        symbol_layer.setDataDefinedProperty("angle", "AZIMUTH")
        symbol.appendSymbolLayer(symbol_layer)

        renderer = QgsSingleSymbolRendererV2(symbol)
        self.thieflayer.setRendererV2(renderer)

    # DIGITIZE LAST TEN LOBS FROM CSV
    def csvLobRefresh(self):
        print "lobrefresh"
        cur_dir = os.path.dirname(os.path.realpath(__file__))

        thief = shapefile.Reader(os.path.join(cur_dir, "data", "thiefsymbolcsvshp.shp"))

        shapes = thief.shapes()
        x, y = (shapes[0].points[0])

        del thief

        w = shapefile.Writer(shapefile.POLYLINE)

        w.field('ID', 'C', '16')
        w.field('LOB', 'N', '8')

        with open(os.path.join(cur_dir, "data", "test.csv")) as line_in:
            csv_lines = list(csv.reader(line_in, delimiter=','))
            reader = csv_lines[len(csv_lines) - 10:]
            for rec in reversed(reader):
                print "lobs"
                no, angle = rec[0], float(rec[5])
                line_len = 10
                angle_rad = math.radians(angle)
                dx = line_len * math.sin(angle_rad)
                dy = line_len * math.cos(angle_rad)
                x2, y2 = x + dx, y + dy
                w.line(parts=[[[x, y], [x2, y2]]])
                w.record(ID=no, LOB=angle)


        w.save(os.path.join(cur_dir, "data", "line_points.shp"))

        self.loblayer.setCacheImage(None)
        self.loblayer.triggerRepaint() # repaint layer upon completion

    # DIGITIZE THIEF SYMBOL FROM CSV
    def csvThiefRefresh(self):
        print "thiefrefresh"
        cur_dir = os.path.dirname(os.path.realpath(__file__))


        file_location = os.path.join(cur_dir, "data", "test.csv")
        out_file = os.path.join(cur_dir, "data", "thiefsymbolcsvshp.shp")
        idd, az, y, x = [], [], [], []

        with open(file_location, 'rb') as csvfile:
            r = list(csv.reader(csvfile, delimiter=','))
            reader = r[len(r) - 1:] #read only top row

            for i, row in reversed(list(enumerate(reader))): #reverse table
                idd.append(str(row[0]))
                az.append(float(row[2]))
                try: # cache last Y value if field empty
                    y.append(float(row[6]))
                    MapExplorer.lastY = float(row[6])
                    print "y field filled"
                except (TypeError, ValueError) as e:
                        y.append(MapExplorer.lastY)
                        print "y field empty"

                try: # cache last X value if field empty
                    x.append(float(row[7]))
                    MapExplorer.lastX = float(row[7])
                    print "x field filled"
                except (TypeError, ValueError) as e:
                        x.append(MapExplorer.lastX)
                        print "x field empty"

                print "appended"


        w = shapefile.Writer(shapefile.POINT)
        w.field('ID', 'N')
        w.field('AZIMUTH', 'N', 12)
        w.field('Y', 'F', 10, 8)
        w.field('X', 'F', 10, 8)

        for j, k in enumerate(x): # write data to shapefile
            w.point(k, y[j])
            w.record(idd[j],az[j],y[j], k )
            print "recorded"

        w.save(out_file)

        self.thieflayer.setCacheImage(None)
        self.thieflayer.triggerRepaint() # repaint layer upon completion


    # SHOW LAYERS WHEN CHECKED
    def showVisibleMapLayers(self):
        layers = []
        if self.actionShowCountriesLayer.isChecked():
            layers.append(QgsMapCanvasLayer(self.countries_layer))
        if self.actionShowBasemapLayer.isChecked():
            layers.append(QgsMapCanvasLayer(self.basemap_layer))
        if self.actionShowLobLayer.isChecked():
            layers.append(QgsMapCanvasLayer(self.loblayer))
        if self.actionShowThiefLayer.isChecked():
            layers.append(QgsMapCanvasLayer(self.thieflayer))
        layers.reverse()
        self.mapCanvas.setLayerSet(layers)

    def showBasemapLayer(self):
        self.showVisibleMapLayers()

    def showThiefLayer(self):
        self.showVisibleMapLayers()

    def showCountriesLayer(self):
        self.showVisibleMapLayers()

    def showLobLayer(self):
        self.showVisibleMapLayers()

    def zoomIn(self):
        self.mapCanvas.zoomIn()

    def zoomOut(self):
        self.mapCanvas.zoomOut()

    def setPanMode(self):
        self.actionPan.setChecked(True)
        self.mapCanvas.setMapTool(self.panTool)

    # ZOOM TO THIEF (YELLOW BUTTON)
    def setExploreMode(self):
        self.mapCanvas.setExtent(self.loblayer.extent())
        self.mapCanvas.setExtent(self.thieflayer.extent())
        self.basemap_layer.triggerRepaint()

    '''def setOpenCSV(self):
        self.actionShowCSV.''' #in progress. option to open thief CSV

# CLICK AND DRAG PAN
class PanTool(QgsMapTool):
    def __init__(self, mapCanvas):
        QgsMapTool.__init__(self, mapCanvas)
        self.setCursor(Qt.OpenHandCursor)
        self.dragging = False

    def canvasMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.canvas().panAction(event)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.canvas().panActionEnd(event.pos())
            self.dragging = False


def main():
    print "main"
    QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX'], True)
    QgsApplication.initQgis()


    app = QApplication(sys.argv)


    window = MapExplorer()
    window.show()
    window.raise_()
    window.loadMap()
    try:
        window.zoomToScale()
    except Exception as f:
        print f
    window.setSymbology()
    window.setPanMode()

    app.exec_()
    app.deleteLater()
    QgsApplication.exitQgis()


if __name__ == "__main__":
    print "if name main"
    main()
