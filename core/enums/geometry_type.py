from enum import Enum


# “point”, “linestring”, “polygon”, “multipoint”,”multilinestring”,”multipolygon”

class GeometryType(Enum):
    POINT = "point"
    LINESTRING = "linestring"

    @staticmethod
    def from_geojson_type(type):
        if type == "Point":
            return GeometryType.POINT
        elif type == "LineString":
            return GeometryType.LINESTRING
        else:
            raise NotImplementedError
