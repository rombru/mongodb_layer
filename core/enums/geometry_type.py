from enum import Enum

from osgeo import ogr


class GeometryType(Enum):
    POINT = "point"
    LINESTRING = "linestring"
    POLYGON = "polygon"
    MULTIPOINT = "multipoint"
    MULTILINESTRING = "multilinestring"
    MULTIPOLYGON = "multipolygon"

    @staticmethod
    def from_wkt(wkt):
        geometry: ogr.Geometry = ogr.CreateGeometryFromWkt(wkt)

        if geometry.GetGeometryType() == ogr.wkbPoint:
            return GeometryType.POINT
        elif geometry.GetGeometryType() == ogr.wkbLineString:
            return GeometryType.LINESTRING
        elif geometry.GetGeometryType() == ogr.wkbPolygon:
            return GeometryType.POLYGON
        elif geometry.GetGeometryType() == ogr.wkbMultiPoint:
            return GeometryType.MULTIPOINT
        elif geometry.GetGeometryType() == ogr.wkbMultiLineString:
            return GeometryType.MULTILINESTRING
        elif geometry.GetGeometryType() == ogr.wkbMultiPolygon:
            return GeometryType.MULTIPOLYGON
        else:
            raise NotImplementedError

    @staticmethod
    def from_geojson_type(type):
        if type == "Point":
            return GeometryType.POINT
        elif type == "LineString":
            return GeometryType.LINESTRING
        elif type == "Polygon":
            return GeometryType.POLYGON
        elif type == "MultiPoint":
            return GeometryType.MULTIPOINT
        elif type == "MultiLineString":
            return GeometryType.MULTILINESTRING
        elif type == "MultiPolygon":
            return GeometryType.MULTIPOLYGON
        else:
            raise NotImplementedError
