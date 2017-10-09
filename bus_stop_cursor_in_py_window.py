'''Script to id and import bus stop signs
that aren't in traffic signs fc, then update
attribution.
*Ran in ArcMap's python window*
Author: Alex Buchans
Date: 05/03/16
'''
import arcpy, os
workspace = r'C:\Users\buchansa\AppData\Roaming\ESRI\Desktop10.1\ArcCatalog\Raleigh_Edit.sde'



# select existing bus signs that aren't within 80ft of route
mxd = arcpy.mapping.MapDocument('current')
lyr = arcpy.mapping.ListLayers(mxd)[1] # RALEIGH.TrafficSigns
lyr.definitionQuery = '"SIGN_TYPE" = \'BUS\''
arcpy.SelectLayerByAttribute_management("RALEIGH.TrafficSigns")
arcpy.SelectLayerByLocation_management("RALEIGH.TrafficSigns", "WITHIN_A_DISTANCE",
                                                      "SystemBusRoutes", "80 Feet",
                                                      "REMOVE_FROM_SELECTION") # 167 features

# create list object and add fac ids (sorted by asec by length)
fac_list = sorted(int(row[0]) for row in arcpy.da.SearchCursor("RALEIGH.TrafficSigns", "FACILITYID"))

# begin edit session
edit = arcpy.da.Editor(workspace)
edit.startEditing(True, True)
edit.startOperation()

# update STATUS field to RETIRED
with arcpy.da.UpdateCursor("RALEIGH.TrafficSigns", "STATUS") as cursor:
        for row in cursor:
            if row[0] != 'RETIRED':
                row[0] = 'RETIRED'
                cursor.updateRow(row)

arcpy.SelectLayerByAttribute_management("RALEIGH.TrafficSigns", "CLEAR_SELECTION")


# include ex bus signs that aren't within 250ft of actual signs
arcpy.SelectLayerByAttribute_management("RALEIGH.TrafficSigns")
arcpy.SelectLayerByLocation_management("RALEIGH.TrafficSigns", "WITHIN_A_DISTANCE", "NEWCATSignLocations,
                                                  "250 Feet", "REMOVE_FROM_SELECTION") # 255 features

# add these fac ids to list object
with arcpy.da.SearchCursor("RALEIGH_TrafficSigns", ["FACILITYID", "STATUS"]) as cursor:
    for row in cursor:
        if row[1] != 'RETIRED':
            fac_list.append(int(row[0]))

# update STATUS to RETIRED
with arcpy.da.UpdateCursor("RALEIGH.TrafficSigns", "STATUS") as cursor:
        for row in cursor:
            if row[0] != 'RETIRED':
                row[0] = 'RETIRED'
                cursor.updateRow(row)

arcpy.SelectLayerByAttribute_management("RALEIGH.TrafficSigns", "CLEAR_SELECTION")

# end edit session
edit.stopOperation()
edit.stopEditing(True)
del edit

# write FacIDs to text file for QCing
with open('C:/Cityworks_GIS_data/qc_facids.txt', 'w') as file:
    for fac in set(fac_list): # set(fac_list) == 268
        file.write(fac)
        file.write('\n')

# or to csv
with open("C:/Cityworks_GIS_data/qc_facids.csv", "w") as csvfile:
   csvfile.write("FAC ID\n")
   for fac in sorted(set(fac_list)):
       csvfile.write(fac)
       csvfile.write("\n")
# append to csv
with open("C:/Cityworks_GIS_data/qc_facids.csv", "a") as csvfile:
   for fac in facs: # from later in script
       csvfile.write(fac)
       csvfile.write("\n")

# ------------------------------------------------------------

# start edit session
edit = arcpy.da.Editor(workspace)
edit.startEditing(True, True)
edit.startOperation()

# select signs that aren't within 250ft of existing bus signs
arcpy.SelectLayerByLocation_management("NEWCATSignLocations")
arcpy.SelectLayerByLocation_management("NEWCATSignLocations", "WITHIN_A_DISTANCE", "RALEIGH.TrafficSigns",
                                                  "250 Feet", "REMOVE_FROM_SELECTION") # 166 Features

#insert new selected signs into existing signs layer
with arcpy.da.InsertCursor("RALEIGH.TrafficSigns", ["SHAPE@", "NOTES"]) as icursor:
    with arcpy.da.SearchCursor("NEWCATSignLocations", ["SHAPE@", "Stop_Name"]) as scursor:
        for row in scursor:
            icursor.insertRow(row)

# get next fac id
next_fac = max([int(row[0]) for row in arcpy.da.SearchCursor("RALEIGH.TrafficSigns", "FACILITYID") if row[0] is not None]) + 1

# update new_signs with standard attributes ***SELECT ALL THE NEWLY ADDED SIGNS FIRST***
with arcpy.da.UpdateCursor("RALEIGH_TrafficSigns", "*") as cursor:
    for row in cursor:
        row[6] = 'BUS'
        row[7] = 'GOOD'
        row[9] = 'BOX CHANNEL'
        row[10] = 'NO'
        row[11] = 'NO'
        row[12] = str(next_fac)
        row[16] = 'ACTIVE'
        row[17] = 'Ground'
        row[18] = 'REGULATORY'
        cursor.updateRow(row)
        next_fac += 1

# grab street attributes from nearest road, then hold and use to populate sign feature attributes
facs = [row[0] for row in arcpy.da.SearchCursor("RALEIGH_TrafficSigns", "FACILITYID")]
arcpy.SelectByAttribute_management("RALEIGH.TrafficSigns", "CLEAR_SELECTION")

# using selected sign features, update each with nearest street attributes
for f in facs:
    arcpy.SelectLayerByAttribute_management("RALEIGH_TrafficSigns", "NEW_SELECTION", '"FACILITYID" = \'{}\''.format(f))
    arcpy.SelectLayerByLocation_management("RALEIGH.PavedStreets", "WITHIN_A_DISTANCE", "RALEIGH_TrafficSigns", "50 Feet", "NEW_SELECTION")
    streets = []
    with arcpy.da.SearchCursor("RALEIGH.PavedStreets", ["STREET", "TP", "BEG_DESC", "END_DESC"]) as cursor:
        for row in cursor:
            streets.append(row)
    if not streets: continue # if no street nearby, skip
    arcpy.SelectLayerByAttribute_management("RALEIGH_TrafficSigns", "NEW_SELECTION", '"FACILITYID" = \'{}\''.format(f))
    with arcpy.da.UpdateCursor("RALEIGH_TrafficSigns", ["ROUTE", "RAHEAD", "RBEHIND"]) as cursor:
        for row in cursor:
            row[0] = streets[0][0] + " " + streets[0][1]
            row[1] = streets[0][2]
            row[2] = streets[0][3]
            cursor.updateRow(row)

# stop edit op here
edit.stopOperation()

# ------------------------------------------------------------
'''Create single bus routes shapefile
from multiple route shapefiles'''

# loop thru shapefiles in folder
arcpy.env.workspace = '' # add directory path here

for shp in arcpy.ListFeatureClasses():
    # check if singlepart
    if sum(1 for row in arcpy.da.SearchCursor(shp, "*")) > 1:
        # prep for creating new shp
        new_shp = os.path.join(os.path.dirname(shp), os.path.basename(shp).split(".")[0]+"_2.shp")
        # if so, run dissolve tool
        arcpy.Dissolve_management(shp, new_shp)
        # add route num field
        arcpy.AddField_management(new_shp, "ROUTE_NM", "TEXT", field_length=50)
        # populate w/ shapefile name
        with arcpy.da.UpdateCursor(new_shp, "ROUTE_NM") as cursor:
            for row in cursor:
                row[0] = os.path.basename(shp).split(".")[0]
                cursor.updateRow(row)
        continue
    if "ROUTE_NM" in [field.name for field in arcpy.ListFields(shp)]:
        continue
    else:
        arcpy.AddField_management(shp, "ROUTE_NM", "TEXT", field_length=50)
        with arcpy.da.UpdateCursor(shp, "ROUTE_NM") as cursor:
            for row in cursor:
                row[0] = os.path.basename(shp).split(".")[0]
                cursor.updateRow(row)

# finally, merge all shps into one, and preserve route num field (field mapping)
field_map = arcpy.FieldMappings()

merge_shps = arpcy.ListFeatureClasses("*_2*")
arcpy.Merge_management(merge_shps, arcpy.env.workspace + "SystemRoutes", field_map)
