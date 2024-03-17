# Mongodb layer

This repository contains a plugin which create layers from a MongoDB datasource.

It does require the installation of "pymongo" package for Python.

## Features
- Select a database, a collection and a geometry field
- Import documents as features
- Filter imported documents
- Limit the number of documents
- Assign the document attributes to each feature
- Support several geometry types (point, linestring, polygon, multipoint, multilinestring and multipolygon)
- The selected geometry field can be at root level, nested in an object, nested in an array
- If the selected geometry field is a list, geometries are combined
- Allow getting a mix of multi and simple geometries from the same collection 

## ToDo
- Support other formats of geometry
- Automatically verify the installation of pymongo
- Support projection with another CRS
- Support async loading of a layer

