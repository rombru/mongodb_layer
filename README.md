# Mongodb layer

This repository contains a plugin which create layers from a MongoDB datasource.

## Requirements
- QGIS 3.0+
- Python 3.7+

If an error occurs, the error message will be displayed in QGIS under the Log Messages panel.

Because MongoDB collections often contain unstructured data, it is quite complicated to test all different cases. If you encounter any issue, please provide a sample of your data so that I can reproduce the problem.

## Features
- Select a database, a collection and a geometry field
- Import documents as features
- Filter imported documents
- Limit the number of documents
- Choose the coordinate system
- Assign the document attributes to each feature
- Support several geometry types (point, linestring, polygon, multipoint, multilinestring and multipolygon)
- Support several format of geometries (GeoJSON, WKT)
- The selected geometry field can be at root level, nested in an object, nested in an array
- If the selected geometry field is a list, geometries are combined
- Allow getting a mix of multi and simple geometries from the same collection 
- The layer is loaded asynchronously

## ToDo
- ...

## Commands
- Release: `git archive --prefix mongodb_layer/ --format=zip --output mongodb_layer.zip HEAD`
- Compile resources: `pyrcc5 -o resources.py resources.qrc`