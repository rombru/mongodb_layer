import uuid

from bson import Decimal128
from qgis._core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY

from .enums.geometry_format import GeometryFormat
from .enums.geometry_type import GeometryType


class MongoDBLayer(QgsVectorLayer):

    def __init__(self, data: list[object], collection: str, geometry_field: str, geometry_type: GeometryType,
                 geometry_format: GeometryFormat):
        super(MongoDBLayer, self). \
            __init__(geometry_type.value,
                     collection + '-' + str(uuid.uuid4())[0:4],
                     "memory")

        self.data = data
        self.collection = collection
        self.geometry_field = geometry_field
        self.geometry_type = geometry_type

        self.startEditing()
        self.add_mongo_db_features(data)
        self.commitChanges()

    def add_mongo_db_features(self, data: list[object]):
        for feature in data:
            qgs_feature = QgsFeature()
            coordinates = feature[self.geometry_field]["coordinates"]
            qgs_feature.setGeometry(self.create_qgs_geometry(coordinates))

            # qgsfeature.setAttributes(self.createAttributes(feature))
            self.addFeature(qgs_feature)

    def create_qgs_geometry(self, coordinates):
        if self.geometry_type == GeometryType.POINT:
            return point_from_coord(coordinates)
        elif self.geometry_type == GeometryType.LINESTRING:
            return QgsGeometry.fromPolylineXY([
                point_from_coord(pt) for pt in coordinates
            ])
        elif self.geometry_type == GeometryType.POLYGON:
            return QgsGeometry.fromPolygonXY([
                [point_from_coord(pt) for pt in ring]
                for ring in coordinates
            ])
        elif self.geometry_type == GeometryType.MULTIPOINT:
            return QgsGeometry.fromMultiPointXY([
                point_from_coord(pt) for pt in coordinates
            ])
        elif self.geometry_type == GeometryType.MULTILINESTRING:
            return QgsGeometry.fromMultiPolylineXY([
                [point_from_coord(pt) for pt in ring]
                for ring in coordinates
            ])
        elif self.geometry_type == GeometryType.MULTIPOLYGON:
            return QgsGeometry.fromMultiPolygonXY([
                [[point_from_coord(pt) for pt in ring]
                 for ring in inner_polygon]
                for inner_polygon in coordinates
            ])


def point_from_coord(coordinates):
    float_coordinates = list(map(get_number_as_float, coordinates))
    return QgsGeometry.fromPointXY(QgsPointXY(*float_coordinates))


def get_number_as_float(num) -> float:
    if isinstance(num, Decimal128):
        return float(num.to_decimal())
    else:
        return num
