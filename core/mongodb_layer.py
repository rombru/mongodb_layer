import uuid
from typing import Dict, Union

from qgis._core import QgsVectorLayer, QgsFeature, QgsGeometry

from .enums.field_type import FieldType
from .enums.geometry_format import GeometryFormat
from .geometry_utils import get_geometry_type, get_geometries_by_feature, geometry_to_qgs_geometry


class MongoDBLayer(QgsVectorLayer):

    def __init__(self, data: list[object], collection: str, geometry_field: str, fields_and_types: Dict[str,FieldType],
                 geometry_format: GeometryFormat):

        self.data = data
        self.collection = collection
        self.geometry_field = geometry_field
        self.geometry_field_type = fields_and_types[geometry_field]
        self.geometry_type = get_geometry_type(data, self.geometry_field, self.geometry_field_type)

        super(MongoDBLayer, self). \
            __init__(self.geometry_type.value,
                     collection + '-' + str(uuid.uuid4())[0:4],
                     "memory")

        self.startEditing()
        self.add_mongo_db_features(data)
        self.commitChanges()

    def add_mongo_db_features(self, data: list[object]):
        for feature in data:
            qgs_feature = QgsFeature()
            qgs_feature.setGeometry(self.create_qgs_geometry(feature, self.geometry_field, self.geometry_field_type))


            # qgsfeature.setAttributes(self.createAttributes(feature))
            self.addFeature(qgs_feature)

    def create_qgs_geometry(self, feature, geometry_field: str, geometry_field_type: FieldType):
        geometries = get_geometries_by_feature(feature, geometry_field, geometry_field_type)
        qgs_geometry: Union[QgsGeometry, None] = None

        for geometry in geometries:
            next_qgs_geometry = geometry_to_qgs_geometry(geometry, self.geometry_type)
            if qgs_geometry:
                qgs_geometry.combine(next_qgs_geometry)
            else:
                qgs_geometry = next_qgs_geometry
