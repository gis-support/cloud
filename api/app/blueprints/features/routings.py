#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app, make_response
from functools import wraps
from app.docs import swagger
from app.db.general import token_required, check_permission, geojson, geojson_single

mod_features = Blueprint("features", __name__)

@mod_features.route('/features', methods=['GET'])
@swagger(__file__, 'docs.features.get.yml')
@token_required
def features():
    if request.method == 'GET':
        name = request.args.get("name")
        error, code = check_permission(name)
        if error:
            return jsonify({"error": error}), code
        return jsonify(geojson(name))

@mod_features.route('/features/<int:fid>', methods=['GET'])
@swagger(__file__, 'docs.features.get.yml')
@token_required
def features_id(fid):
    if request.method == 'GET':
        name = request.args.get("name")
        error, code = check_permission(name)
        if error:
            return jsonify({"error": error}), code
        msg, code = geojson_single(name, fid)
        return jsonify(msg), code