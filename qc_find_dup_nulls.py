"""QC Script to check for duplicate FacilityIDs
in a feature class
"""
import arcpy
from collections import Counter


##for count in Counter([row[0] for row in arcpy.da.SearchCursor(
##                     "RALEIGH.TrafficSigns", "FACILITYID")]).items():
##    if count[1] > 1:
##        print(count)

feature_class = (r'C:\Users\buchansa\AppData\Roaming\ESRI\Desktop10.1'
            r'\ArcCatalog\Raleigh.sde\RALEIGH.ROW_Inventory\RALEIGH.TrafficSigns')
field1 = "FACILITYID"
field0 = "OBJECTID"

# function to identify all duplicate values for a field in the same feature class
def find_dups(feature_class, field):
    return [count for count in Counter([row[0] for row in arcpy.da.SearchCursor(feature_class, field)]).items()
            if count[1] > 1]

# function to identify all null values for a field in the same feature class
def find_nulls(feature_class, field0, field1):
    for value in [(row[0], row[1]) for row in arcpy.da.SearchCursor(feature_class, [field0, field1])]:
        if value[1] is None:
            return value[0]


if __name__ == '__main__':
    #print("These are the duplicate FacIDs: {}".format(find_duplicates(feature_class, field1)))
    print("These are the duplicate FacIDs: ")
    for facid in find_duplicates(feature_class, field1):
          print(facid)
    print("-"*20)
    print("These are the features with null FacIDs: {}".format(find_nulls(feature_class, field0, field1)))
    print("Done...")


"""This code was run in the ArcMap python window.
It is addition QC on a feature class"""
# find lowercase ROUTE values to fix
with arcpy.da.SearchCursor("RALEIGH.TrafficSigns", ["ROUTE", "FACILITYID"]) as cursor:
    for row in cursor:
        if row[0] is None: pass
        elif any(r.islower() for r in row[0]):
            print row

# find any features with attributes 'delete' in NOTES field
import re
check = re.compile(r'delete')

for row in arpcy.da.SearchCursor("RALEIGH.TrafficSigns", ["OBJECTID", "NOTES"]):
    if row[1] is not None:
        if check.search(row[1]):
            print row[0] #prints OBJECTID

# find all features that 'need field check' listed
check = re.compile(r'Need Field Check')

field_check = [(check.search(row[1]),row) for row in arcpy.da.SearchCursor("RALEIGH_TrafficSigns",
                ["OBJECTID", "NOTES"]) if row[1] is not None]
needs_check = [value for value in field_check if value[0] is not None]
