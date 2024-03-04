from bson import Decimal128
from qgis._core import QgsGeometry, QgsPointXY

from .enums.field_type import FieldType
from .enums.geometry_type import GeometryType


def get_geometry_type(data: list[object], geometry_field: str, geometry_field_type: FieldType):
    geojson_geometry = get_any_geometry(data, geometry_field, geometry_field_type)

    if not geojson_geometry:
        return GeometryType.POINT
    else:
        return GeometryType.from_geojson_type(geojson_geometry["type"])


def get_any_geometry(data: list[object], geometry_field: str, geometry_field_type: FieldType):
    for feature in data:
        geometry = get_geometries_by_feature(feature, geometry_field, geometry_field_type)
        if geometry: return geometry

    return None


def get_geometries_by_feature(feature, geometry_field: str, geometry_field_type: FieldType):
    geometries = []

    if geometry_field_type == FieldType.ROOT:
        geometries.append(feature[geometry_field])
    elif geometry_field_type == FieldType.OBJECT:
        geometry_field_split = geometry_field.split(".")
        geometries.append(feature[geometry_field_split[0]][geometry_field_split[1]])
    elif geometry_field_type == FieldType.ARRAY:
        geometry_field_split = geometry_field.split(".")
        array_in_feature = feature[geometry_field_split[0]]
        for feature_part in array_in_feature:
            geometries.append(feature_part[geometry_field_split[1]])

    return filter(None, geometries)


def geometry_to_qgs_geometry(geometry, geometry_type: GeometryType):
    coordinates = geometry["coordinates"]

    if geometry_type == GeometryType.POINT:
        return get_point_from_coord(coordinates)
    elif geometry_type == GeometryType.LINESTRING:
        return QgsGeometry.fromPolylineXY([
            get_point_from_coord(pt) for pt in coordinates
        ])
    elif geometry_type == GeometryType.POLYGON:
        return QgsGeometry.fromPolygonXY([
            [get_point_from_coord(pt) for pt in ring]
            for ring in coordinates
        ])
    elif geometry_type == GeometryType.MULTIPOINT:
        return QgsGeometry.fromMultiPointXY([
            get_point_from_coord(pt) for pt in coordinates
        ])
    elif geometry_type == GeometryType.MULTILINESTRING:
        return QgsGeometry.fromMultiPolylineXY([
            [get_point_from_coord(pt) for pt in ring]
            for ring in coordinates
        ])
    elif geometry_type == GeometryType.MULTIPOLYGON:
        return QgsGeometry.fromMultiPolygonXY([
            [[get_point_from_coord(pt) for pt in ring]
             for ring in inner_polygon]
            for inner_polygon in coordinates
        ])


def get_point_from_coord(coordinates):
    float_coordinates = list(map(get_number_as_float, coordinates))
    return QgsGeometry.fromPointXY(QgsPointXY(*float_coordinates))


def get_number_as_float(num) -> float:
    if isinstance(num, Decimal128):
        return float(num.to_decimal())
    else:
        return num
