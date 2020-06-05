import json
import arcpy
import requests

#Need to get a Mapbox API key in order to run this code.
#Field that is added will be called "Elevation"
#You can change the units that the elevation measurement are in by changing the request URL format.
#in_kps = The point feature class you want to assign elevations to.
  #No idea if this works for multipart points - didn't do any testing.

def giveKPsElevation(in_kps,mapquest_key):
    baseURL = r"http://open.mapquestapi.com/elevation/v1/profile?key={}&shapeFormat=raw&latLngCollection=".format(mapquest_key)
    ptCount = int(arcpy.GetCount_management(in_kps)[0])
    if ptCount >= 10000:
        raise SystemError('Can only get elevations for 10,000 or fewer points. Points provided = {}'.format(ptCount))
    foundPts = []
    with arcpy.da.SearchCursor(in_kps,"SHAPE@XY",spatial_reference=arcpy.SpatialReference(4326)) as curs:
        for row in curs:
            foundPts.append("{},{}".format(row[0][1],row[0][0]))
    ptsString = ','.join(foundPts)
    elevationPts = requests.get(baseURL+ptsString).json()
    
    if 'Elevation' not in [f.name for f in arcpy.ListFields(in_kps)]:
        arcpy.AddField_management(in_kps,'Elevation','DOUBLE')

    cnt = 0    
    with arcpy.da.UpdateCursor(in_kps,"Elevation") as kpCurs:
        for row in kpCurs:
            row[0] = elevationPts['elevationProfile'][cnt]['height']
            cnt+=1
            kpCurs.updateRow(row)
