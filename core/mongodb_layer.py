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

        self.startEditing()
        self.addMongoDBFeatures(data)
        self.commitChanges()

    def addMongoDBFeatures(self, data: list[object]):
        for feature in data:
            qgs_feature = QgsFeature()
            coordinates = list(map(get_number_as_double, feature["geometry"]["coordinates"]))
            # coordinates = [float(str(d)) for d in coordinates]
            qgs_feature.setGeometry(QgsGeometry.fromPointXY(
                QgsPointXY(*coordinates)
            ))
            # qgsfeature.setAttributes(self.createAttributes(feature))
            self.addFeature(qgs_feature)




def get_number_as_double(num) -> float:
    if isinstance(num, Decimal128):
        return float(num.to_decimal())
    else:
        return num