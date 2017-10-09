"""
Script to update the crosswalks layer
Date: 6/21/16
"""
import arcpy

#create Grid to track areas checked
arcpy.SelectLayerByLocation_management("RALEIGH.RFD_MAP_PAGE_GRID", "INTERSECT", "WAKE.JURISDICTION")
arcpy.CopyFeatures_management("RALEIGH.RFD_MAP_PAGE_GRID", "C:\Cityworks_GIS_data\RaleighGrid.shp")
#add field to track checked
arcpy.AddField_management("RaleighGrid", "CHECKED", "TEXT", "", "", 5)
#confirm field
print([field.name for field in arcpy.Describe("RaleighGrid").fields])
## [u'FID', u'Shape', u'ID', u'NAME', u'SHAPE_AREA', u'SHAPE_LEN', u'CHECKED']

###ADD POINTS manually###
### NEED to QC layer for attribution: ie FACILITYID values, CONDITION spelled properly, etc
"""
This is how I calced these attributes
Date: 08/29/16
"""
workspace = r'C:\Users\buchansa\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Raleigh_Edit.sde'
edit = arcpy.da.Editor(workspace)
edit.startEditing(True, True)
edit.startOperation()

arcpy.SelectLayerByAttribute_management("RALEIGH.Crosswalks", "NEW_SELECTION", '"FACILITYID" IS NULL')

with arcpy.da.UpdateCursor("RALEIGH.Crosswalks", ["OBJECTID", "UNIQUEID", "FACILITYID"]) as cursor:
    for row in cursor:
        oid = row[0]
        row[1] = oid  # calc over oid to UNIQUEID field
        row[2] = oid  # calc over oid to FACILITYID field
        cursor.updateRow(row)

with arcpy.da.UpdateCursor("RALEIGH.Crosswalks", ["CONDITION", "TYPE"]) as cursor:
    for row in cursor:
        row[0] = "GOOD"
        if row[1] is None:
            row[1] = "STANDARD"
        cursor.updateRow(row)

"""
Update ROUTE, RAHEAD, RBEHIND attributes by grabbing street attributes from nearest road,
then hold and use to populate sign feature attributes
"""
# ***DO THIS BLOCK DURING LUNCH*** *TURNED OFF BACKGROUND PROCESSING IN GEOPROCESSING OPTIONS MENU - MUCH FASTER*
facs = [row[0] for row in arcpy.da.SearchCursor("RALEIGH.Crosswalks", "FACILITYID")]
arcpy.SelectByAttribute_management("RALEIGH.Crosswalks", "CLEAR_SELECTION")

# use facs list to select each crosswalk and populate street attribution
for f in facs:
    arcpy.SelectLayerByAttribute_management("RALEIGH.Crosswalks", "NEW_SELECTION", '"FACILITYID" = \'{}\''.format(f))
    arcpy.SelectLayerByLocation_management("RALEIGH.PavedStreets", "WITHIN_A_DISTANCE", "RALEIGH.Crosswalks", "50 Feet", "NEW_SELECTION")
    streets = []
    with arcpy.da.SearchCursor("RALEIGH.PavedStreets", ["STREET", "TP", "BEG_DESC", "END_DESC"]) as cursor:
        for row in cursor:
            streets.append(row)
    if not streets: continue # if no street nearby, skip
    arcpy.SelectLayerByAttribute_management("RALEIGH.Crosswalks", "NEW_SELECTION", '"FACILITYID" = \'{}\''.format(f))
    with arcpy.da.UpdateCursor("RALEIGH.Crosswalks", ["ROUTE", "RAHEAD", "RBEHIND"]) as cursor:
        for row in cursor:
            row[0] = streets[0][0] + " " + streets[0][1]
            row[1] = streets[0][2]
            row[2] = streets[0][3]
            cursor.updateRow(row)

edit.stopOperation()
edit.stopEditing(True)
