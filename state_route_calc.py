"""Command line script to calculate nearest state route
for point feature class | either creates join or updates"""
import arcpy



input_fc = arcpy.GetParameterAsText(0)
join_fc = arcpy.GetParameterAsText(1)
output_fc = arcpy.GetParameterAsText(2)
version = arcpy.GetParameterAsText(3)

if version == 'Create':
    try:
        # create spatial join
        arcpy.SpatialJoin_analysis(input_fc, join_fc, output_fc, "JOIN_ONE_TO_MANY",
                                   match_option="WITHIN_A_DISTANCE", search_radius="50 Feet")

        # join traffic signs w/ spatial join layer, on obj id | this updates the input's field
        arcpy.JoinField_management(input_fc, "OBJECTID", output_fc, "OBJECTID", ["Rte_Nm"])
    except:
        print(arcpy.GetMessages())

elif version == 'Update':
    try:
        # create filtered layer to be updated
        arcpy.MakeFeatureLayer_management(input_fc, "trafsignslyr", where_clause='"Rte_Nm" IS NULL')

        # create spatial join
        arcpy.SpatialJoin_analysis("trafsignslyr", join_fc, output_fc, "JOIN_ONE_TO_MANY",
                                   "KEEP_COMMON", match_option="WITHIN_A_DISTANCE", search_radius="50 Feet")

        features = dict()
        with arcpy.da.SearchCursor(output_fc, ["FACILITYID", "Rte_Nm"]) as cursor:
            for row in cursor:
                features[row[0]] = row[1]

        with arcpy.da.UpdateCursor("Traffic Signs", ["FACILITYID", "Rte_Nm"]) as cursor:
            for row in cursor:
                if row[0] in features:
                    row[1] = features[row[0]]
                    cursor.updateRow(row)
    except:
        print(arcpy.GetMessages())

arcpy.AddMessage("All done")
