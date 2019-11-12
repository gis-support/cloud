#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app, make_response
from functools import wraps
from app.docs import swagger
from app.db.general import token_required, list_layers, create_table, table_exists, remove_table, create_mvt_tile, check_permission
import jwt
import uuid
import gdal
import tempfile
import os.path as op
import binascii
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

@mod_layers.route('/layers', methods=['GET', 'POST', 'DELETE'])
@swagger(__file__, 'docs.layers.get.yml')
@token_required
def layers():
    if request.method == 'GET':
        layers = list_layers(request.user)
        return jsonify({"layers": layers})
    elif request.method == 'DELETE':
        name = request.args.get("name")
        error, code = check_permission(name)
        if error:
            return jsonify({"error": error}), code
        remove_table(name)
        return jsonify({"layers": "{} removed".format(name)})
    else:
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
        return jsonify({"layers": {"name": name, "features": count_features}}), 201

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
