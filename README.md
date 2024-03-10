# Mongodb layer

This repository contains a plugin which create layers from a MongoDB datasource.

It does require the installation of "pymongo" package for Python.

## Features
- Point, linestring and polygon support
- Multipoint, multilinestring and multipolygon support
- Filtering documents
- Limit the number of documents
- Nested geometry field support
- List of geometries by feature support
- Allow mixing multi and simple geometries in the same layer

## ToDo
- Add the attributes to each feature
- Support other formats of geometry
- Automatically verify the installation of pymongo
- Support projection with another CRS
- Support async loading of a layer

