"""Script to select and buffer underground fiber segments
and create new shapefile that's dated to send to 811 locator"""
import arcpy
import datetime


input_fc = (r'C:\Users\buchansa\AppData\Roaming\ESRI\Desktop10.3'
            r'\ArcCatalog\Raleigh.sde\RALEIGH.ROW_Inventory\RALEIGH.Fibers')
#to run on command line - enter directory path
output_workspace = arcpy.GetParameterAsText(0)
outfile = output_workspace + '\Fiber_' + datetime.datetime.now().strftime('%m%d%y') + '.shp'

try:
    #select layer of underground fiber segments
    arcpy.MakeFeatureLayer_management(input_fc, "ug_layer", "LAYER = 'FiberUG'")
    #buffer layer by 50 feet, and save to new layer
    arcpy.Buffer_analysis("ug_layer", outfile, "50 Feet", "FULL", "ROUND", "ALL")
    print(arcpy.GetMessages())
except:
    print(arcpy.GetMessages())
