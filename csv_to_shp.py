"""Script to create a feature class of points or line
from csv or text file
"""
import arcpy
import csv

input_table = arcpy.GetParameterAsText(0)
output_fc = arcpy.GetParameterAsText(1)
lat = arcpy.GetParameterAsText(2)
lon = arcpy.GetParameterAsText(3)

# spatial reference
# spat_ref = arcpy.GetParameterAsText(4) # spatial reference setting in script

# determine if fc will be points or lines
feature_type = arcpy.GetParameterAsText(4) # domain: 'Points', 'Line'

if feature_type == 'Points':
    # Easier, just make xy layer
    try:
        # make xy event layer
        arcpy.MakeXYEventLayer_management(input_table, lat, lon, output_fc, spat_ref)
    except:
        print(arcpy.GetMessages())

else:
    try:
        gps_tracks = []
        with open(input_table) as csvfile:
            gps_track = csv.DictReader(csvfile) # delimeter arg might not be valid
            rows = list(gps_track)
            for row in rows[1:]:
                gps_tracks.append((row[lat], row[lon]))

        # create polyline geometry
        array = arcpy.Array([arcpy.Point(row[0], row[1]) for row in gps_tracks])
        polyline = arcpy.Polyline(array)

        with arcpy.da.InsertCursor(output_fc, ("SHAPE@")) as cursor:
            cursor.insertRow((polyline,))
    except:
        print(arcpy.GetMessages())

print(arcpy.AddMessage("Finished creating feature class"))
