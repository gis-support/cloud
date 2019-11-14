#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app, make_response
from functools import wraps
from app.docs import swagger
from app.db.general import token_required, cloud_decorator, create_mvt_tile, layer_decorator
from app.helpers.cloud import Cloud
from app.helpers.layer import Layer
import jwt
import uuid
import gdal
import tempfile
import os.path as op
import binascii
from shapely.geometry import shape
from osgeo import osr
from osgeo import ogr

mod_layers = Blueprint("layers", __name__)

FIELD_TYPES = {
    "String": "varchar",
    "Integer": "integer",
    "Real": "real",
    "DateTime": "timestamp",
    "Date": "timestamp"
}

@mod_layers.route('/layers', methods=['GET', 'POST'])
@swagger(__file__, 'docs.layers.get.yml')
@token_required
@cloud_decorator
def layers(cloud):
    if request.method == 'GET':
        return jsonify({"layers": cloud.get_layers()})
    elif request.method == 'POST':
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "file is required"}), 401
        name = request.form.get("name")
        if not name:
            return jsonify({"error": "name is required"}), 401
        if cloud.layer_exists(name):
            return jsonify({"error": "table already exists"}), 401
        file_path = op.join(tempfile.mkdtemp(), file.filename)
        file.save(file_path)
        source = ogr.Open(file_path, 0)
        layer = source.GetLayer()
        if layer.GetSpatialRef().GetAuthorityCode(None) != "4326":
            return jsonify({"error": "epsg not 4326"}), 409
        ldefn = layer.GetLayerDefn()
        test_geom_type_feature = layer.GetNextFeature()
        layer.ResetReading()
        fields = [{
            "name": "geometry",
            "type": "geometry({}, 4326)".format(test_geom_type_feature.GetGeometryRef().GetGeometryName())
        }]
        for n in range(ldefn.GetFieldCount()):
            fdefn = ldefn.GetFieldDefn(n)
            fields.append({
                'name': fdefn.name,
                'type': FIELD_TYPES[fdefn.GetTypeName()],
            })
        with current_app._db.atomic() as transaction:
            cloud = Cloud({"app": current_app, "user": request.user})
            cloud.create_layer(name, fields)
            with tempfile.SpooledTemporaryFile(mode='w') as tfile:
                columns = list(map(lambda f: f['name'], fields))
                count_features = 0
                for feature in layer:
                    the_geom = feature.GetGeometryRef()
                    feature_string = ''
                    for idx, column  in enumerate(columns):
                        # Pierwszy wiersz to geometria
                        if idx == 0:
                            feature_string += 'SRID=4326;%s\t' % feature.GetGeometryRef().ExportToWkt()
                        elif idx + 1 != len(columns):
                            feature_string += '%s\t' % feature.GetField(column)
                        else:
                            feature_string += '%s\n' % feature.GetField(column)
                    count_features += 1
                    tfile.write(feature_string)
                tfile.seek(0)
                cur = current_app._db.cursor()
                cur.copy_from(tfile, '"{}"'.format(name), null='None', columns=list(map(lambda c: '"{}"'.format(c), columns)))
        layer = Layer({"app": current_app, "user": request.user, "name": name})
        return jsonify({"layers": {"name": layer.name, "features": layer.count(), "id": layer.lid}}), 201

@mod_layers.route('/layers/<lid>', methods=['DELETE'])
@swagger(__file__, 'docs.layers.id.delete.yml')
@token_required
@layer_decorator
def layers_id(layer, lid):
    layer = Layer({"app": current_app, "user": request.user, "lid": lid})
    layer.delete()
    return jsonify({"layers": "{} deleted".format(layer.name)})

@mod_layers.route('/layers/<lid>/features', methods=['GET', 'POST'])
@swagger(__file__, 'docs.features.get.yml')
@token_required
@layer_decorator
def features(layer, lid):
    layer = Layer({"app": current_app, "user": request.user, "lid": lid})
    if request.method == 'GET':
        return jsonify(layer.as_geojson())
    elif request.method == 'POST':
        data = request.get_json(force=True)
        geometry = 'SRID=4326;{}'.format(shape(data['geometry']).wkt)
        columns = []
        values = []
        for k, v in data['properties'].items():
            if k in layer.columns():
                columns.append(k)
                values.append(v)
        layer.add_feature(columns, values)
        return jsonify({"layers": {"name": layer.name, "features": layer.count(), "id": layer.lid}}), 201

@mod_layers.route('/layers/<lid>/features/<int:fid>', methods=['GET', 'PUT', 'DELETE'])
@swagger(__file__, 'docs.features.get.yml')
@token_required
@layer_decorator
def features_id(layer, lid, fid):
    layer = Layer({"app": current_app, "user": request.user, "lid": lid})
    if request.method == 'GET':
        return layer.as_geojson_by_fid(fid)
    elif request.method == 'PUT':
        data = request.get_json(force=True)
        geometry = 'SRID=4326;{}'.format(shape(data['geometry']).wkt)
        columns = []
        values = []
        for k, v in data['properties'].items():
            if k in layer.columns():
                columns.append(k)
                values.append(v)
        layer.edit_feature(fid, columns, values)
        return jsonify({"layers": {"name": layer.name, "features": layer.count(), "id": layer.lid}}), 200
    elif request.method == 'DELETE':
        layer.delete_feature(fid)
        return jsonify({"layers": {"name": layer.name, "features": layer.count(), "id": layer.lid}}), 200

@mod_layers.route('/mvt/<int:z>/<int:x>/<int:y>', methods=['GET'])
def tiles(z=0, x=0, y=0):
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "invalid layer name"})
    tile = create_mvt_tile(z, x, y, name)
    if not tile:
        return ('', 204)
    response = make_response(tile)
    response.headers['Content-Type'] = "application/octet-stream"
    return response
