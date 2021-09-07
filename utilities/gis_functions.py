'''
Created on Aug 3, 2021

@author: brett_wood
'''
from utilities.sql_utils import *

def queryPolygonEquality(polygon1, polygon2):
    
    polygon1 = str(polygon1)
    polygon2 = str(polygon2)
    
    query = ("select st_equals(" + polygon1 +"," + polygon2 +")")
    equal_polygons = executeSql(query)[0]
    
    return equal_polygons 


def queryPolygonRules(outputs):
    
    valid_polygon_decimals = True
    
    for i in range(0,len(outputs)):
        output_shape = outputs[i][2].decode('utf-8')
        query = "select st_astext(st_geomfromtext('" + output_shape + "',4326),6) = '" + output_shape + "';"
        valid_polygon_decimals = executeSql(query)[0]
        if valid_polygon_decimals == False:
            break
    
    return valid_polygon_decimals


def queryPolygonAreaMeters (polygon):
    
    polygon = str(polygon)
    
    query = ("select st_area(st_geomfromtext('" + polygon +"',4326)::geography)")
    area = executeSql(query)[0]
    
    return area 


def queryUnionPolygonAreaMeters (unioned_polygon):
    
    polygon = str(unioned_polygon)
    
    query = ("select st_area(" + unioned_polygon +"::geography)")
    area = executeSql(query)[0]
    
    return area 
