import uuid
from typing import Dict, Union, List

from PyQt5.QtCore import QVariant
from qgis._core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFields

from .enums.field_nesting import FieldNesting
from .enums.geometry_format import GeometryFormat
from .enums.geometry_type import GeometryType
from .field_utils import get_field_type
from .geometry_utils import get_geometry_type, get_geometries_by_feature, geometry_to_qgs_geometry


class MongoDBLayer(QgsVectorLayer):
    data: List[Dict]
    collection: str
    geometry_field: str
    geometry_field_nesting: FieldNesting
    geometry_type: GeometryType
    qgs_fields: QgsFields

    def __init__(self, data: List[Dict], collection: str, geometry_field: str, fields: Dict[str, FieldNesting],
                 geometry_format: GeometryFormat, epsg: str):

        self.data = data
        self.collection = collection
        self.geometry_field = geometry_field
        self.geometry_format = geometry_format
        self.geometry_field_nesting = fields[geometry_field]
        self.geometry_type = get_geometry_type(data, self.geometry_field, self.geometry_field_nesting, geometry_format)

        super(MongoDBLayer, self). \
            __init__(self.get_uri(self.geometry_type, epsg), collection + '-' + str(uuid.uuid4())[0:4],"memory")

        if data:
            self.startEditing()
            self.qgs_fields = self.get_qgs_fields(data, fields)
            self.add_qgs_fields_to_layer(self.qgs_fields)
            self.add_mongo_db_features(data, self.qgs_fields)
            self.commitChanges()

    def get_uri(self, geometry_type, epsg):
        if not epsg:
            return geometry_type.value
        else:
            return geometry_type.value + "?crs=epsg:" + epsg

    def get_qgs_fields(self, data, fields):
        qgs_fields = QgsFields()
        for field, nesting in fields.items():
            if nesting == FieldNesting.ROOT:
                qgs_fields.append(QgsField(field, get_field_type(data, field)))

        return qgs_fields

    def add_qgs_fields_to_layer(self, qgs_fields: QgsFields):
        for qgs_field in qgs_fields.toList():
            self.addAttribute(qgs_field)

    def add_mongo_db_features(self, data: List[Dict], qgs_fields: QgsFields):
        i = 0
        for feature in data:
            qgs_feature = QgsFeature()
            qgs_feature.setGeometry(self.create_qgs_geometry(feature, self.geometry_field, self.geometry_field_nesting))
            qgs_feature.setFields(qgs_fields)
            qgs_feature.setAttributes(self.create_attributes(feature, qgs_fields))
            self.addFeature(qgs_feature)
            i = i+1

    def create_attributes(self, feature: dict, qgs_fields: QgsFields):
        attributes = []

        for qgs_field in qgs_fields.toList():
            value = feature.get(qgs_field.name())
            if value:
                attributes.append(self.create_attribute(value, qgs_field))
            else:
                attributes.append(None)

        return attributes

    def create_attribute(self, value, qgs_field: QgsField):
        if qgs_field.type() in [QVariant.Int, QVariant.Double]:
            return value
        else:
            return str(value)

    def create_qgs_geometry(self, feature, geometry_field: str, geometry_field_nesting: FieldNesting):
        geometries = get_geometries_by_feature(feature, geometry_field, geometry_field_nesting)
        qgs_geometry: Union[QgsGeometry, None] = None

        for geometry in geometries:
            next_qgs_geometry = geometry_to_qgs_geometry(geometry, self.geometry_format)
            if qgs_geometry:
                qgs_geometry.combine(next_qgs_geometry)
            else:
                qgs_geometry = next_qgs_geometry

        return qgs_geometry
