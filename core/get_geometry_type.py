from .enums.geometry_type import GeometryType


def get_geometry_type(data: list[object], geometry_field: str):
    if len(data) == 0:
        return GeometryType.POINT
    else:
        return GeometryType.from_geojson_type(data[0][geometry_field]["type"])