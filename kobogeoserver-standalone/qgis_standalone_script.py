from qgis.core import *
from PyQt5.QtCore import *
from qgis.utils import *
qgs = QgsApplication([], False)
qgs.initQgis()

layerFields = QgsFields()
layerFields.append(QgsField('ID', QVariant.Int))
layerFields.append(QgsField('Value', QVariant.Double))
layerFields.append(QgsField('Name', QVariant.String))

fn = '/Users/saimanojappalla/Downloads/audiotour/survey/new.shp'
writer = QgsVectorFileWriter(fn, 'UTF-8', layerFields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem('EPSG:4326'), 'ESRI Shapefile')
qgs.exitQgis()