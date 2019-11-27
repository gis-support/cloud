#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.docs import path_by
from app.db.general import token_required, layer_decorator
from app.helpers.layer import Layer
from shapely.geometry import shape

mod_features = Blueprint("features", __name__)


@mod_features.route('/layers/<lid>/features', methods=['POST'])
@swag_from(path_by(__file__, 'docs.features.post.yml'), methods=['POST'])
@token_required
@layer_decorator(permission="write")
def features_post(layer, lid):
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


@mod_features.route('/layers/<lid>/features/<int:fid>', methods=['GET', 'PUT', 'DELETE'])
@swag_from(path_by(__file__, 'docs.features.id.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.features.id.put.yml'), methods=['PUT'])
@swag_from(path_by(__file__, 'docs.features.id.delete.yml'), methods=['DELETE'])
@token_required
def features_id(lid, fid):
    if request.method == 'GET':
        """
        Get feature by ID with default permission
        Returns GeoJSON
        """
        @layer_decorator(permission="read")
        def get(layer, lid=None):
            return layer.as_geojson_by_fid(fid)
        return get(lid=lid)

    elif request.method == 'PUT':
        """
        Edit feature by ID with write permission
        Returns layer properties
        """
        @layer_decorator(permission="write")
        def put(layer, lid=None):
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
        return put(lid=lid)

    elif request.method == 'DELETE':
        """
        Delete feature by ID with write permission
        Returns layer properties
        """
        @layer_decorator(permission="write")
        def delete(layer, lid=None):
            layer.delete_feature(fid)
            return jsonify({"layers": {"name": layer.name, "features": layer.count(), "id": layer.lid}}), 200
        return delete(lid=lid)
