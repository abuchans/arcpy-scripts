'''Prints out formatted calculated values
for entered feature class. Run from the
command line'''
import arcpy


input_fc = arcpy.GetParameterAsText(0)
field_calc = arcpy.GetParameterAsText(1)
value = arcpy.GetParameterAsText(2)
stat = arcpy.GetParameterAsText(3)

try:
    arcpy.AddMessage("Calculating total {}....".format(value))
    field_values = []
    with arcpy.da.SearchCursor(input_fc, "{}".format(field_calc)) as cursor:
        for row in cursor:
            field_values.append(row[0])
    if stat == 'count':
        total = len(field_values)
    elif value.lower() == 'feet' and stat == 'length':
        total = sum(field_values)
    elif value.lower() == 'miles' and stat == 'length':
        total = sum(field_values) / 5280

    arcpy.AddMessage("Total: {} {}".format(total, value))
except:
    print(arcpy.GetMessages())
