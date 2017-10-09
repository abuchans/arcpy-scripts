"""Script to delete shapefiles out of a folder
that meet criteria from parameter list"""
import arcpy
import re

workspace = '' # add directory path
numbers = []  # list of numbers to flag for deletion
fc_list = arcpy.ListFeatureClasses()

# iterate thru shps
for fc in fc_list:
    # just get numbers after '_' and before '.shp'
    fc_name = re.split("[_.]", fc)[1]
    # check if any nums in numbers list is in file name
    if fc_name in numbers:
        arcpy.Delete_management(fc)
    else:
        pass
