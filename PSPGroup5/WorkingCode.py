import arcpy
import os


### Creates shapefile from user input and creates PDF with a simple layout ##

# Get current directory for geodatabase and convert csv file to point shapefile #
cwd = os.getcwd()

arcpy.env.workspace = cwd + r"\PSPGroup5\PSPGrp5.gdb"
pointfile = arcpy.management.XYTableToPoint(cwd + r"\data.csv", r"\PointData\surveypoints.shp", "Longitude", "Latitude")
arcpy.conversion.FeatureClassToGeodatabase(cwd + r"\PointData\surveypoints.shp", cwd + "PSPGroup5\PSPGrp5.gdb")

# Set project to work on layout and create layer file from shapefile #
aprx = arcpy.mp.ArcGISProject(cwd + r"\PSPGroup5\PSPGrp5.aprx")

in_layer = cwd + r"\PSPGroup5\PSPGrp5.gdb\surveypoints" 
layers_out = "Benchmarks" 
output_location = cwd + r"\{}.lyrx".format(layers_out)

arcpy.MakeFeatureLayer_management(in_layer, "Benchmarks")
arcpy.SaveToLayerFile_management ("Benchmarks" , layers_out)

# Add layer file to map at the top of the content pane #
insertLyr = arcpy.mp.LayerFile(output_location)
m = aprx.listMaps("*")[0]
refLyr = m.listLayers("*")[0]
m.insertLayer(refLyr, insertLyr, "BEFORE")

# Save copy so newly created layer is retrievable in project copy, change aprx variable to new project #
aprx.save()

# Apply symbology to the point layer #
lyr = m.listLayers("Benchmarks")[0]
sym = lyr.symbology
# if lyr.isFeatureLayer and hasattr(sym, "renderer"):
sym.renderer.symbol.applySymbolFromGallery("Circle 4")
sym.renderer.symbol.size = 12
lyr.symbology = sym

# Set map frame extent to point layer and zoom out so the points are not at the edges of the frame #
lyt = aprx.listLayouts("PointLayout")[0]
mf = lyt.listElements("mapframe_element", "MyMapFrame")[0]
mf.camera.setExtent(mf.getLayerExtent(lyr))
m.defaultCamera = mf.camera
mf.camera.scale *= 1.08

# # Add point file to legend item #
# legend = lyt.listElements("LEGEND_ELEMENT", "Legend")[0]
# legend.addItem(lyr)

lyt.exportToPDF(cwd + r"\PlottedPoints.pdf")

aprx.save()
del aprx

print("File Exported")
