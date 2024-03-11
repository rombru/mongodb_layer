from PyQt5.QtCore import QVariant


def get_field_type(data: list[object], field: str) -> QVariant:
    for feature in data:
        if field in feature:
            return get_field_type_by_field_data(feature[field])

def get_field_type_by_field_data(field_data: any):
    if type(field_data) is int:
        return QVariant.Int
    elif type(field_data) is float:
        return QVariant.Double
    else:
        return QVariant.String
