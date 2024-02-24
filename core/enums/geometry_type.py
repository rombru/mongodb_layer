from enum import Enum


# “point”, “linestring”, “polygon”, “multipoint”,”multilinestring”,”multipolygon”

class GeometryType(Enum):
    POINT = "point"
