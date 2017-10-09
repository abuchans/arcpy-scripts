"""Code for a esri Python AddIn toolbar.
Creates a toolbar with two buttons and a
combo box"""
import arcpy
import pythonaddins
import sys

class CalcFacID(object):
    """Implementation for PythonAddIns_addin.button2 (Button)
    This button updates a single selected point based on location"""
    def __init__(self):
        self.enabled = True
        self.checked = False
        self.fac_id = max(int(row[0]) for row in arcpy.da.SearchCursor("RALEIGH.TrafficSigns", "FACILITYID")
                          if row[0] is not None)
    def onClick(self):
        def calc_signcat(value):
            if value:
                if value.startswith('R'):
                    if value.startswith('R7'):
                        return 'PARKING'
                    return 'REGULATORY'
                elif value.startswith('D'):
                    return 'DIRECTIONAL'
                elif value.startswith('W'):
                    return 'WARNING'
                elif value.startswith('S'):
                    return 'SCHOOL'
                else:
                    return None
            else:
                return None

        edit = arcpy.da.Editor(r'C:\Users\buchansa\AppData\Roaming\ESRI\Desktop10.1\ArcCatalog\Raleigh_Edit.sde')
        edit.startEditing(True, True)
        edit.startOperation()

        row_dict = {"FACILITYID": None, "SIGN_CATEGORY": None, "ROUTE": None, "RAHEAD": None, "RBEHIND": None}

        with arcpy.da.SearchCursor(r"Base Layers\Block Numbers", ["STREET", "TP", "BEG_DESC", "END_DESC"]) as cursor:
            # confirm just one selected, then add to streets list
            count = sum(1 for row in cursor)
            if count == 1:
                cursor.reset()
                row = cursor.next()
                streets = list(row)
            else:
                pythonaddins.MessageBox("Please select one street segment", "Problem", 0)
                sys.exit()

        self.fac_id += 1
        row_dict["FACILITYID"] = str(self.fac_id)
        row_dict["SIGN_CATEGORY"] = calc_signcat(arcpy.da.SearchCursor("RALEIGH.TrafficSigns", ["SIGN_TYPE"]).next()[0])
        row_dict["ROUTE"], row_dict["RAHEAD"], row_dict["RBEHIND"] = streets[0] + ' ' + streets[1], streets[2], streets[3]
                                                                # or ' '.join(x for x in streets[:2])

       # update selected traffic signs feature
        with arcpy.da.UpdateCursor("RALEIGH.TrafficSigns",
                                   ["ROUTE", "RAHEAD", "RBEHIND", "FACILITYID", "SIGN_CATEGORY"]
                                   ) as cursor:
            # confirm just one selected, then update
            count = sum(1 for row in cursor)
            if count == 1:
                cursor.reset()
                for row in cursor:
                    row[0] = row_dict["ROUTE"]
                    row[1] = row_dict["RAHEAD"]
                    row[2] = row_dict["RBEHIND"]
                    row[3] = row_dict["FACILITYID"]
                    row[4] = row_dict["SIGN_CATEGORY"]
                    cursor.updateRow(row)
            else:
                # more than one feature was selected if here
                pythonaddins.MessageBox("Please select just one sign", "Problem", 0)
                sys.exit()
        edit.stopOperation()

        """alternative to select street by location [may be quicker]"""
        arcpy.SpatialJoin_analysis("RALEIGH.TrafficSigns", r"Base Layers\Block Numbers", r"C:\Cityworks_GIS_data\JoinLayer.shp"
                                   "JOIN_ONE_TO_MANY", match_option="WITHIN_A_DISTANCE", search_radius="25 Feet")
        values = [row for row in arcpy.da.SearchCursor("JoinLayer", ["STREET", "TP", "BEG_DESC", "END_DESC"])]
        row_dict["ROUTE"], row_dict["RAHEAD"], row_dict["RBEHIND"] = values[0][0] + ' ' + values[0][1], values[0][2], values[0][3]

        with arcpy.da.UpdateCursor("RALEIGH.TrafficSigns",
                                   ["ROUTE", "RAHEAD", "RBEHIND", "FACILITYID", "SIGN_CATEGORY"]
                                   ) as cursor:
            last_row = cursor.next()

            last_row[0] = row_dict["ROUTE"]
            last_row[1] = row_dict["RAHEAD"]
            last_row[2] = row_dict["RBEHIND"]
            last_row[3] = row_dict["FACILITYID"]
            last_row[4] = row_dict["SIGN_CATEGORY"]
            cursor.updateRow(last_row)

        arcpy.Delete_management("JoinLayer")

class CalcStateRoute(object):
    """Implementation for PythonAddIns_addin.button (Button)
    This button calculates the state route a selected sign feature
    is nearest to"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        row_dict = {"STATEROUTE": None}

        state_route = arcpy.SelectLayerByLocation_management("Rd_Wake_Clip",
                                                             "WITHIN_A_DISTANCE",
                                                             "RALEIGH.TrafficSigns",
                                                             "50 Feet")

        with arcpy.da.SearchCursor(state_route, ["STREET_NAME"]) as cursor:
            for row in cursor:
                row_dict["STATEROUTE"] = str(row[0])

        with arcpy.da.UpdateCursor("RALEIGH.TrafficSigns",
                                   ("STATEROUTE")
                                   ) as cursor:
            # confirm just one feature selected, then update
            count = sum(1 for row in cursor)
            if count == 1:
                cursor.reset()
                    for row in cursor:
                        row[0] = row_dict["STATEROUTE"]
                        cursor.updateRow(row)

        # unselect state route feature that was selected as a side effect
        arcpy.SelectLayerByAttribute_management("Rd_Wake_Clip", "CLEAR_SELECTION")

class ComboBoxClass11(object):
    """Implementation for PythonAddIns_addin.combobox (ComboBox)
    This combo box will select and zoom to a feature with a match for
    the unique facility id field"""
    def __init__(self):
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWW'
        self.width = 'WWWWWW'
        self.text = None
    def onSelChange(self, selection):
        pass
    def onEditChange(self, text):
        self.text = text
    def onFocus(self, focused):
        pass
    def onEnter(self):
        my_mxd = arcpy.mapping.MapDocument("CURRENT")
        # enable zoomToSelectedFeatures method
        df = arcpy.mapping.ListDataFrames(my_mxd)[0]
        lyr = arcpy.mapping.Layer("RALEIGH.TrafficSigns")

        try:
            arcpy.da.SearchCursor(lyr, ["FACILITYID"], where_clause='"FACILITYID" = \'{}\''.format(self.text)).next()[0]
            feature = arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION",
                                                              "FACILITYID = " + "'" + self.text + "'")
            # select stacked points, if applicable
            arcpy.SelectLayerByLocation_management(feature, "ARE_IDENTICAL_TO", lyr,
                                                   "0 Feet", "ADD_TO_SELECTION")
            df.zoomToSelectedFeatures()
        except:
            # no match for facility id
            pythonaddins.MessageBox('Enter a valid Fac ID', 'WRONG', 0)
    def refresh(self):
        pass

    """alternative to above [may be quicker] ***try this one***"""
    def onEnter(self):
        my_mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(my_mxd)[0]

        arcpy.SelectLayerByAttribute_management("RALEIGH_TrafficSigns", "NEW_SELECTION",
                                                          '"FACILITYID = \'{}\''.format(self.text))
        if not arcpy.Describe("RALEIGH_TrafficSigns").FIDSet:
            pythonaddins.MessageBox('Enter a valid Fac ID', 'WRONG', 0)
            sys.exit()
        arcpy.SelectLayerByLocation_management("RALEIGH_TrafficSigns", "ARE_IDENTICAL_TO", "RALEIGH_TrafficSigns",
                                                   "0 Feet", "ADD_TO_SELECTION")
        df.zoomToSelectedFeatures()
        df.scale = 1000.00
        arcpy.RefreshActiveView()

    def refresh(self):
        pass
