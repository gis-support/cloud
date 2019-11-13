#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app, make_response
from functools import wraps
from app.docs import swagger
from app.db.general import token_required, list_layers, create_table, table_exists, remove_table, create_mvt_tile, geojson, geojson_single, hashed, unhashed, permission_required, list_table_columns, add_feature_to_layer, edit_feature, delete_feature
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
def layers():
    if request.method == 'GET':
        layers = list_layers(request.user)
        return jsonify({"layers": layers})
    elif request.method == 'POST':
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "file is required"}), 401
        name = request.form.get("name")
        if not name:
            return jsonify({"error": "name is required"}), 401
        if table_exists(name):
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
            create_table(name, fields, request.user)
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
        return jsonify({"layers": {"name": name, "features": count_features, "id": hashed(name)}}), 201

@mod_layers.route('/layers/<lid>', methods=['DELETE'])
@swagger(__file__, 'docs.layers.id.delete.yml')
@token_required
@permission_required
def layers_id(lid):
    layer_name = unhashed(lid)
    remove_table(layer_name)
    return jsonify({"layers": "{} removed".format(layer_name)})

@mod_layers.route('/layers/<lid>/features', methods=['GET', 'POST'])
@swagger(__file__, 'docs.features.get.yml')
@token_required
@permission_required
def features(lid):
    layer_name = unhashed(lid)
    if request.method == 'GET':
        return jsonify(geojson(layer_name))
    elif request.method == 'POST':
        data = request.get_json(force=True)
        layer_columns = list_table_columns(layer_name)
        geometry = 'SRID=4326;{}'.format(shape(data['geometry']).wkt)
        columns = []
        values = []
        for k, v in data['properties'].items():
            if k in layer_columns:
                columns.append(k)
                values.append(v)
        count_features = add_feature_to_layer(layer_name, columns, values)
        return jsonify({"layers": {"name": layer_name, "features": count_features, "id": lid}}), 201

@mod_layers.route('/layers/<lid>/features/<int:fid>', methods=['GET', 'PUT', 'DELETE'])
@swagger(__file__, 'docs.features.get.yml')
@token_required
@permission_required
def features_id(lid, fid):
    layer_name = unhashed(lid)
    if request.method == 'GET':
        msg, code = geojson_single(layer_name, fid)
        return jsonify(msg), code
    elif request.method == 'PUT':
        data = request.get_json(force=True)
        layer_columns = list_table_columns(layer_name)
        geometry = 'SRID=4326;{}'.format(shape(data['geometry']).wkt)
        columns = []
        values = []
        for k, v in data['properties'].items():
            if k in layer_columns:
                columns.append(k)
                values.append(v)
        count_features = edit_feature(layer_name, fid, columns, values)
        return jsonify({"layers": {"name": layer_name, "features": count_features, "id": lid}}), 200
    elif request.method == 'DELETE':
        count_features = delete_feature(layer_name, fid)
        return jsonify({"layers": {"name": layer_name, "features": count_features, "id": lid}}), 200

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
