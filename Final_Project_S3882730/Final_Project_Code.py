from qgis.utils import iface
from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import processing

#Setting of geodatabase path.
GBD_Path = 'C:\\Users\\user\\Desktop\\RMIT_2021_2\\Geospatial Programming\\Final Project\\Sample_Geodatabase.gdb\\'
#Definition of initial supporting data layers from the sample geodatabase.
boundaryLayer = QgsVectorLayer(GBD_Path + 'BOUNDARY.shp', "LOCALITY_BOUNDARY", "ogr") #Locality boundaries.
conservationLayer = QgsVectorLayer(GBD_Path + 'PUBLIC_CONSERVATION.shp', "PUBLIC_CONSERVATION", "ogr") #Conservation Sites.
hydroLayer = QgsVectorLayer(GBD_Path + 'HY_WATER_AREA_POLYGON.shp', "HY_WATER_AREA_POLYGON", "ogr") #Water Bodies.
urbanLayer = QgsVectorLayer(GBD_Path + 'URBAN_AREA.shp', "URBAN_AREA", "ogr") #Urban Area.
roadLayer = QgsVectorLayer(GBD_Path + 'MAJOR_ROADS.shp', "MAJOR_ROADS", "ogr") #Main Roads
railroadLayer = QgsVectorLayer(GBD_Path + 'TR_RAIL.shp', "TR_RAIL", "ogr") #Railways
treeLayer = QgsVectorLayer(GBD_Path + 'TREE_DENSITY_AREA.shp', "TREE_DENSITY_AREA", "ogr") #High Tree Density Areas.
#CRS Setting: GDA2020 / MGA zone 55 (Standard of the GDB data)
crs = QgsCoordinateReferenceSystem("EPSG:7855")
#Creation of buffers for Conservation, Hydrology, Urban, Roads, Railroads with their respective buffering values in meters.
processing.run('native:buffer', {"INPUT": conservationLayer, "DISTANCE": 400, "OUTPUT": (GBD_Path + 'CONSERVATION_BUFFER.shp'), 'DISSOLVE' : True})
processing.run('native:buffer', {"INPUT": hydroLayer, "DISTANCE": 200, "OUTPUT": (GBD_Path + 'HYDRO_BUFFER.shp'), 'DISSOLVE' : True})
processing.run('native:buffer', {"INPUT": urbanLayer, "DISTANCE": 500, "OUTPUT": (GBD_Path + 'URBAN_BUFFER.shp'), 'DISSOLVE' : True})
processing.run('native:buffer', {"INPUT": roadLayer, "DISTANCE": 300, "OUTPUT": (GBD_Path + 'ROAD_BUFFER.shp'), 'DISSOLVE' : True})
processing.run('native:buffer', {"INPUT": railroadLayer, "DISTANCE": 300, "OUTPUT": (GBD_Path + 'RAILROAD_BUFFER.shp'), 'DISSOLVE' : True})
#Creation of a negative-value buffer for the boundaries layer in order to limit the analysis area to 300m away from the locality's boundaries.
processing.run('native:buffer', {"INPUT": boundaryLayer, "DISTANCE": -300, "OUTPUT": (GBD_Path + 'NEGATIVE_BUFFER.shp'), 'DISSOLVE' : True}) 
#Definition of resulting buffer layers.
conservationBufferLayer = QgsVectorLayer(GBD_Path + 'CONSERVATION_BUFFER.shp', "CONSERVATION_BUFFER", "ogr") 
hydroBufferLayer = QgsVectorLayer(GBD_Path + 'HYDRO_BUFFER.shp', "HYDRO_BUFFER", "ogr")
urbanBufferLayer = QgsVectorLayer(GBD_Path + 'URBAN_BUFFER.shp', "URBAN_BUFFER", "ogr")
roadBufferLayer = QgsVectorLayer(GBD_Path + 'ROAD_BUFFER.shp', "ROAD_BUFFER", "ogr")
railroadBufferLayer = QgsVectorLayer(GBD_Path + 'RAILROAD_BUFFER.shp', "RAILROAD_BUFFER", "ogr")
negativeBufferLayer = QgsVectorLayer(GBD_Path + 'NEGATIVE_BUFFER.shp', "NEGATIVE_BUFFER", "ogr") 
#Clipping the negative-buffered boundaries layer with the high tree density areas layer.
processing.run('native:difference', {'INPUT': negativeBufferLayer, 'OUTPUT': (GBD_Path + 'CLIP_T.shp'), 'OVERLAY': treeLayer})
clipTLayer = QgsVectorLayer(GBD_Path + 'CLIP_T.shp', "CLIP_T", "ogr")
#Clipping the resulting layer with the buffered conservation areas layer.
processing.run('native:difference', {'INPUT': clipTLayer, 'OUTPUT': (GBD_Path + 'CLIP_TC.shp'), 'OVERLAY': conservationBufferLayer})
clipTCLayer = QgsVectorLayer(GBD_Path + 'CLIP_TC.shp', "CLIP_TC", "ogr")
#Clipping the resulting layer with the buffered water bodies layer.
processing.run('native:difference', {'INPUT': clipTCLayer, 'OUTPUT': (GBD_Path + 'CLIP_TCH.shp'), 'OVERLAY': hydroBufferLayer})
clipTCHLayer = QgsVectorLayer(GBD_Path + 'CLIP_TCH.shp', "CLIP_TCH", "ogr")
#Clipping the resulting layer with the buffered urban area layer.
processing.run('native:difference', {'INPUT': clipTCHLayer, 'OUTPUT': (GBD_Path + 'CLIP_TCHU.shp'), 'OVERLAY': urbanBufferLayer})
clipTCHULayer = QgsVectorLayer(GBD_Path + 'CLIP_TCHU.shp', "CLIP_TCHU", "ogr")
#Clipping the resulting layer with the buffered roads layer.
processing.run('native:difference', {'INPUT': clipTCHULayer, 'OUTPUT': (GBD_Path + 'CLIP_TCHUR.shp'), 'OVERLAY': roadBufferLayer})
clipTCHURLayer = QgsVectorLayer(GBD_Path + 'CLIP_TCHUR.shp', "CLIP_TCHUR", "ogr")
#Clipping the resulting layer with the buffered rail-roads layer. Final clipping operation.
processing.run('native:difference', {'INPUT': clipTCHURLayer, 'OUTPUT': (GBD_Path + 'FINAL_CLIP.shp'), 'OVERLAY': railroadBufferLayer})
finalClipLayer = QgsVectorLayer(GBD_Path + 'FINAL_CLIP.shp', "FINAL_CLIP", "ogr")
#Division of the shape resulting from the final clipping operation into single parts.
processing.run('native:multiparttosingleparts', {'INPUT': finalClipLayer, 'OUTPUT': (GBD_Path + 'SINGLE_PARTS.shp')})
singlePartsLayer = QgsVectorLayer(GBD_Path + 'SINGLE_PARTS.shp', "SINGLE_PARTS", "ogr")
#Addition of geometry attributes to know the area of every part from the resulting singlePartsLayer.
processing.run('qgis:exportaddgeometrycolumns', {'INPUT': singlePartsLayer, 'OUTPUT': (GBD_Path + 'SINGLE_PARTS_ATTRIBUTES.shp'), 'CALC_METHOD' : 0})
singlePartsAttributesLayer = QgsVectorLayer(GBD_Path + 'SINGLE_PARTS_ATTRIBUTES.shp', "SINGLE_PARTS_ATTRIBUTES", "ogr")
#Extraction of geometries with an area of over 5 hectares and definition of final result layer.
processing.run('native:extractbyattribute', {'FIELD': 'area_2', 'INPUT': singlePartsAttributesLayer, 'OUTPUT': (GBD_Path + 'FINAL_RESULT.shp'), 'OPERATOR': 2, 'VALUE': '50000'})
finalResultLayer = QgsVectorLayer(GBD_Path + 'FINAL_RESULT.shp', "FINAL_RESULT", "ogr")
#Loading of base boundary layer and final prospective area results layer. Only these two layers added for visualization clarity purposes.
QgsProject.instance().addMapLayer(boundaryLayer)
QgsProject.instance().addMapLayer(finalResultLayer)

