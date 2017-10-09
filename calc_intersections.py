# calc intersection owners
'''Calc intersection classification
Ran spatial join prior to this, used
field mapping to populate "Names" field with
attributes from nearby streets
'''
import arcpy

with arcpy.da.UpdateCursor("RALEIGH_Intersections_SJoin2", ["Names", "Int_Class"]) as cursor:
    for row in cursor:
        # if any part in row[0] matches the Public strings
        if any(x in row[0] for x in ['COR', 'State']):
            if 'Private' in row[0]:
                row[1] = 'Public/Private'
            else:
                row[1] = 'Public/Public'
        else:
            row[1] = 'Private/Private'
        cursor.updateRow(row)

# calc totals for each
from collections import Counter

Counter(row[0] for row in arcpy.da.SearchCursor("RALEIGH_Intersections_SJoin2", "Int_Class"))
# >>> Counter({u'Public/Public': 7445, u'Public/Private': 1354, u'Private/Private': 563})
