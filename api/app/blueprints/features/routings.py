#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.docs import path_by
from app.db.general import token_required, layer_decorator
from app.helpers.layer import Layer, TYPES
from shapely.geometry import shape

mod_features = Blueprint("features", __name__)


@mod_features.route('/layers/<lid>/features', methods=['POST'])
@swag_from(path_by(__file__, 'docs.features.post.yml'), methods=['POST'])
@token_required
@layer_decorator(permission="write")
def features_post(layer, lid):
    data = request.get_json(force=True)
    geometry = 'SRID=4326;{}'.format(shape(data['geometry']).wkt)
    columns = ['geometry']
    values = [geometry]
    for k, v in data['properties'].items():
        if k in layer.columns():
            columns.append(k)
            values.append(v)
    feature = layer.add_feature(columns, values)
    return jsonify(feature), 201


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
            try:
                return layer.as_geojson_by_fid(fid)
            except ValueError:
                return jsonify({"error": "feature not exists"}), 404
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
            columns = ['geometry']
            values = [geometry]
            columns_with_types = layer.columns(with_types=True)
            for k, v in data['properties'].items():
                if k in list(columns_with_types.keys()):
                    columns.append(k)
                    values.append(v)
            try:
                feature = layer.edit_feature(
                    fid, columns, values, columns_with_types)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            return jsonify(feature), 200
        return put(lid=lid)

    elif request.method == 'DELETE':
        """
        Delete feature by ID with write permission
        Returns layer properties
        """
        @layer_decorator(permission="write")
        def delete(layer, lid=None):
            layer.delete_feature(fid)
            return jsonify({"fid": fid}), 200
        return delete(lid=lid)
