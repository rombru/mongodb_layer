from qgis._core import QgsGeometry, QgsPointXY

from .enums.field_nesting import FieldNesting
from .enums.geometry_format import GeometryFormat
from .enums.geometry_type import GeometryType


def get_geometry_type(data: list[dict], geometry_field: str, geometry_field_nesting: FieldNesting,
                      geometry_format: GeometryFormat):
    raw_geometry = get_any_geometry(data, geometry_field, geometry_field_nesting)

    if not raw_geometry:
        return GeometryType.POINT
    elif geometry_format == GeometryFormat.GEOJSON:
        return GeometryType.from_geojson_type(raw_geometry["type"])
    else:
        return GeometryType.from_wkt(raw_geometry)


def get_any_geometry(data: list[dict], geometry_field: str, geometry_field_nesting: FieldNesting):
    for feature in data:
        geometries = get_geometries_by_feature(feature, geometry_field, geometry_field_nesting)
        if geometries and len(geometries) > 0: return geometries[0]

    return None


def get_geometries_by_feature(feature: dict, geometry_field: str, geometry_field_nesting: FieldNesting):
    geometries = []

    geometries_or_geometry_lists = []
    if geometry_field_nesting == FieldNesting.ROOT:
        root = feature.get(geometry_field)
        if root:
            geometries_or_geometry_lists.append(root)
    elif geometry_field_nesting == FieldNesting.OBJECT:
        geometry_field_split = geometry_field.split(".")
        root = feature.get(geometry_field_split[0])
        nested = root.get(geometry_field_split[1])
        if nested:
            geometries_or_geometry_lists.append(nested)
    elif geometry_field_nesting == FieldNesting.ARRAY:
        geometry_field_split = geometry_field.split(".")
        root_array = feature.get(geometry_field_split[0])
        if root_array:
            for feature_array_elem in root_array:
                nested = feature_array_elem.get(geometry_field_split[1])
                if nested:
                    geometries_or_geometry_lists.append(nested)

    for elem in geometries_or_geometry_lists:
        if type(elem) is list:
            for geometry in elem:
                geometries.append(geometry)
        else:
            geometries.append(elem)

    return list(filter(None, geometries))


def geometry_to_qgs_geometry(geometry, geometry_format: GeometryFormat):
    if geometry_format == GeometryFormat.WKT:
        return QgsGeometry.fromWkt(geometry)
    else:
        return geojson_geometry_to_qgs_geometry(geometry)


def geojson_geometry_to_qgs_geometry(geometry):
    coordinates = geometry["coordinates"]

    geometry_type = get_geometry_type_by_geometry(geometry)

    if geometry_type == GeometryType.POINT:
        return QgsGeometry.fromPointXY(
            get_point_from_coord(coordinates)
        )
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


def get_geometry_type_by_geometry(geometry):
    coordinates = geometry["coordinates"]
    geometry_type = GeometryType.from_geojson_type(geometry["type"])

    if geometry_type == GeometryType.POLYGON and type(coordinates[0][0][0]) is list:
        return GeometryType.MULTIPOLYGON
    if geometry_type == GeometryType.MULTIPOLYGON and type(coordinates[0][0][0]) is not list:
        return GeometryType.POLYGON

    if geometry_type == GeometryType.LINESTRING and type(coordinates[0][0]) is list:
        return GeometryType.MULTILINESTRING
    if geometry_type == GeometryType.MULTILINESTRING and type(coordinates[0][0]) is not list:
        return GeometryType.LINESTRING

    if geometry_type == GeometryType.POINT and type(coordinates[0]) is list:
        return GeometryType.MULTIPOINT
    if geometry_type == GeometryType.MULTIPOINT and type(coordinates[0]) is not list:
        return GeometryType.POINT

    return geometry_type


def get_point_from_coord(coordinates):
    float_coordinates = list(map(get_number_as_float, coordinates))
    return QgsPointXY(*float_coordinates)


def get_number_as_float(num) -> float:
    from bson import Decimal128  # noqa

    if isinstance(num, Decimal128):
        return float(num.to_decimal())
    else:
        return num
