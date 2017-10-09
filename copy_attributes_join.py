"""Copy attributes from one table to another,
using a spatial join
"""
import arcpy


input_fc = arcpy.GetParameterAsText(0)
join_fc = arcpy.GetParameterAsText(1)
output_fc = arcpy.GetParameterAsText(2)
fields = [field for field in arcpy.GetParameterAsText(3).split(",")] # include target id field and value field
fields_2 = [field for field in arcpy.GetParameterAsText(4).split(",")] # include oid field and calc field

try:
    # run spatial join
    arcpy.SpatialJoin_analysis(input_fc, join_fc, output_fc)

    # store field values to transfer in dict
    values_dict = {row[0]: row[1:] for row in arcpy.da.SearchCursor(output_fc, fields)}

    # run update cursor on original fc to calc the values over
    with arcpy.da.UpdateCursor(input_fc, fields_2) as cursor:
        for row in cursor:
            obj_id = row[0]
            if obj_id in values_dict:
                row[1] = values_dict[obj_id]
                cursor.updateRow(row)

except:
    print(arcpy.GetMessages())
