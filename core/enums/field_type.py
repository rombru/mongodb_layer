from enum import Enum


class FieldType(Enum):
    ROOT = "root"
    ARRAY = "array"
    OBJECT = "object"

    @staticmethod
    def from_str(label):
        if label == FieldType.ROOT.value:
            return FieldType.ROOT
        elif label == FieldType.ARRAY.value:
            return FieldType.ARRAY
        elif label == FieldType.OBJECT.value:
            return FieldType.OBJECT
        else:
            raise NotImplementedError
