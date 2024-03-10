from enum import Enum


class FieldNesting(Enum):
    ROOT = "root"
    ARRAY = "array"
    OBJECT = "object"

    @staticmethod
    def from_str(label):
        if label == FieldNesting.ROOT.value:
            return FieldNesting.ROOT
        elif label == FieldNesting.ARRAY.value:
            return FieldNesting.ARRAY
        elif label == FieldNesting.OBJECT.value:
            return FieldNesting.OBJECT
        else:
            raise NotImplementedError
