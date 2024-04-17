# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MongoDBLayerDockWidget
                                 A QGIS plugin
 This plugin gives the possibility to create a layer from MongoDB datasource
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-02-17
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Romain Bruyère
        email                : rom.bruyere@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import asyncio
import json
import os
import re
import traceback
from typing import Optional, Dict

from PyQt5.QtWidgets import QPlainTextEdit, QPushButton, QComboBox, QLineEdit
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis._core import QgsProject, QgsMessageLog, Qgis

from .enums.field_nesting import FieldNesting
from .enums.geometry_format import GeometryFormat
from .get_attribute_aggregation_pipeline import get_attribute_aggregation_pipeline
from .mongodb_layer import MongoDBLayer

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mongodb_layer_dockwidget_base.ui'))


class MongoDBLayerDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()
    loop: asyncio.AbstractEventLoop

    mongo_client: object
    connectionTextEdit: QPlainTextEdit
    connectionButton: QPushButton
    databaseBox: QComboBox
    collectionBox: QComboBox
    geometryFieldBox: QComboBox
    geometryFormatBox: QComboBox
    queryTextEdit: QPlainTextEdit
    limitEdit: QLineEdit
    epsgEdit: QLineEdit
    addLayerButton: QPushButton

    connection_string: str
    db: str
    collection: str
    geometry_field: str
    geometry_format: GeometryFormat
    fields: Dict[str, FieldNesting]

    def __init__(self, loop, parent=None):
        """Constructor."""
        super(MongoDBLayerDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.loop = loop
        self.setupUi(self)
        self.init_layout()

    def init_layout(self):
        self.connectionButton.clicked.connect(self.connection_button_clicked)
        self.databaseBox.activated[str].connect(self.database_box_change)
        self.collectionBox.activated[str].connect(self.collection_box_change)
        self.geometryFieldBox.activated[str].connect(self.geometry_field_box_change)
        self.geometryFormatBox.activated[str].connect(self.geometry_format_box_change)
        self.addLayerButton.clicked.connect(self.add_layer_button_clicked)

        self.geometryFormatBox.addItems([GeometryFormat.GEOJSON.value, GeometryFormat.WKT.value])
        self.geometryFormatBox.setCurrentIndex(-1)

    def connection_button_clicked(self):
        self.databaseBox.setEnabled(False)
        self.databaseBox.clear()
        self.collectionBox.setEnabled(False)
        self.collectionBox.clear()
        self.geometryFieldBox.setEnabled(False)
        self.geometryFieldBox.clear()
        self.geometryFormatBox.setEnabled(False)
        self.geometryFormatBox.setCurrentIndex(-1)
        self.addLayerButton.setEnabled(False)

        self.connection_string = self.connectionTextEdit.toPlainText()

        from pymongo import MongoClient  # noqa
        self.mongo_client = MongoClient(self.connection_string, serverSelectionTimeoutMS=2000)

        dbs = sorted(self.mongo_client.list_database_names())
        if dbs:
            self.databaseBox.addItems(dbs)
            self.databaseBox.setCurrentIndex(-1)
            self.databaseBox.setEnabled(True)

    def database_box_change(self):
        self.collectionBox.setEnabled(False)
        self.collectionBox.clear()
        self.geometryFieldBox.setEnabled(False)
        self.geometryFieldBox.clear()
        self.geometryFormatBox.setEnabled(False)
        self.geometryFormatBox.setCurrentIndex(-1)
        self.addLayerButton.setEnabled(False)

        self.db = self.databaseBox.currentText()
        collections = sorted(self.mongo_client[self.db].list_collection_names())
        if collections:
            self.collectionBox.addItems(collections)
            self.collectionBox.setCurrentIndex(-1)
            self.collectionBox.setEnabled(True)

    def collection_box_change(self):
        self.geometryFieldBox.setEnabled(False)
        self.geometryFieldBox.clear()
        self.geometryFormatBox.setEnabled(False)
        self.geometryFormatBox.setCurrentIndex(-1)
        self.addLayerButton.setEnabled(False)

        self.collection = self.collectionBox.currentText()
        raw_fields = self.get_fields()
        self.fields = self.to_sorted_fields_with_nesting_type(raw_fields)

        self.geometryFieldBox.addItems(self.fields.keys())
        self.geometryFieldBox.setCurrentIndex(-1)
        self.geometryFieldBox.setEnabled(True)

    def get_fields(self):
        cursor = self.mongo_client[self.db][self.collection].aggregate(get_attribute_aggregation_pipeline)
        document: Optional = cursor.try_next()
        fields: [str] = document["keys"] if document is not None else []
        return fields

    def to_sorted_fields_with_nesting_type(self, keys):
        attribute_types_map = {}
        for key in keys:
            type_key_pair = key.split(":")
            attribute_types_map[type_key_pair[1]] = FieldNesting.from_str(type_key_pair[0])

        return dict(sorted(attribute_types_map.items()))

    def geometry_field_box_change(self):
        self.geometry_field = self.geometryFieldBox.currentText()
        self.geometryFormatBox.setEnabled(True)
        self.geometryFormatBox.setCurrentIndex(-1)
        self.addLayerButton.setEnabled(False)

    def geometry_format_box_change(self):
        self.geometry_format = GeometryFormat.from_str(self.geometryFormatBox.currentText())
        self.addLayerButton.setEnabled(True)

    def add_layer_button_clicked(self):
        query = self.queryTextEdit.toPlainText()
        if not query:
            query = "{}"

        limit = self.limitEdit.text()
        if not limit:
            limit = "1000"

        epsg = self.epsgEdit.text()

        fut = asyncio.run_coroutine_threadsafe(self.add_layer(query, limit, epsg), self.loop)
        try:
            fut.result()
        except:
            e = fut.exception()
            tb = traceback.format_exc()
            print("exception: ", tb)
            QgsMessageLog.logMessage(tb, level=Qgis.Critical)
            QgsMessageLog.logMessage('{}: {}'.format(type(e).__name__, e), level=Qgis.Critical)

    async def add_layer(self, query, limit, epsg):
        json_query = json.loads(self.replace_simple_quote(self.double_quote_json_keys(query)))
        data = list(self.mongo_client[self.db][self.collection].find(json_query).limit(int(limit)))

        layer = MongoDBLayer(data, self.collection, self.geometry_field, self.fields, self.geometry_format, epsg)
        QgsProject.instance().addMapLayer(layer, False)
        QgsProject.instance().layerTreeRoot().insertLayer(0, layer)

    def double_quote_json_keys(self, json_string):
        return re.sub('([{,]\s*)([^"\':]+)(\s*:)', "\g<1>\"\g<2>\"\g<3>", json_string)

    def replace_simple_quote(self, json_string):
        json_string = re.sub('([{,]\s*)(\')([^\']+)(\')(\s*:)', "\g<1>\"\g<3>\"\g<5>", json_string)
        json_string = re.sub('(:\s*)(\')([^\']+)(\')([},]\s*)', "\g<1>\"\g<3>\"\g<5>", json_string)
        return json_string

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
