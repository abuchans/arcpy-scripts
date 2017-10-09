'''Extract spatial features from multiple .dgn CAD files
within a directory, and create shapefiles from them'''
import arcpy, os, string

input_workspace = arcpy.GetParameterAsText(0)
output_workspace = arcpy.GetParameterAsText(1)

try:
    # walk through directory containing .dgn files
    for dirpath, dirnames, filenames in arcpy.da.Walk(input_workspace, type="Polyline"):
        for filename in filenames:
            # create name string from .dgn filename
            splitFile = os.path.split(dirpath)
            cadName = string.split(splitFile[1], "\\")
            finalNameList = ''.join(cadName)
            changeName = string.replace(finalNameList, "-", "_")
            finalName = os.path.splitext(changeName)[0]
            # create shapefile with def query for relevant features
            arcpy.FeatureClassToFeatureClass_conversion(str(os.path.join(dirpath, filename)), output_workspace, finalName, ' "Layer" IN(\'Prop Aerial Fiber Optic Cable _B\', \'Exist Conduit _B\', \'Prop Conduit _B\', \'Prop Directional Drill Conduit _B\', \'Prop Jack and Bore Conduit _B\') ')

except:
    print arcpy.GetMessages()
