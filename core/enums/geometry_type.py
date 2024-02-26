from enum import Enum


class GeometryType(Enum):
    POINT = "point"
    LINESTRING = "linestring"
    POLYGON = "polygon"
    MULTIPOINT = "multipoint"
    MULTILINESTRING = "multilinestring"
    MULTIPOLYGON = "multipolygon"

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
