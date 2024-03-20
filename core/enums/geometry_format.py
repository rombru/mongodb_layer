from enum import Enum


class GeometryFormat(Enum):
    GEOJSON = "GeoJSON"
    WKT = "WKT"

    @staticmethod
    def from_str(label):
        if label == GeometryFormat.GEOJSON.value:
            return GeometryFormat.GEOJSON
        elif label == GeometryFormat.WKT.value:
            return GeometryFormat.WKT
        else:
            raise NotImplementedError
