#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.docs import path_by
from app.db.general import token_required, layer_decorator, admin_only
from app.helpers.layer import Layer
from app.blueprints.rdos.analysis.models import Settings
import os

mod_analysis = Blueprint("analysis", __name__)


@mod_analysis.route('/analysis/settings', methods=['GET', 'PUT'])
@swag_from(path_by(__file__, 'docs.settings.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.settings.put.yml'), methods=['PUT'])
@token_required
def settings():
    if request.method == 'GET':
        return jsonify({"settings": Settings.get_settings()})

    elif request.method == 'PUT':
        @admin_only
        def put():
            Settings.update_settings(request.get_json(force=True))
            return jsonify({"settings": Settings.get_settings()})
        return put()


@mod_analysis.route('/analysis/distance/<lid>/<int:fid>', methods=['POST'])
@swag_from(path_by(__file__, 'docs.distance.post.yml'), methods=['POST'])
@token_required
def analysis_distance(lid, fid):

    @layer_decorator(permission="read")
    def post(layer, lid=None, fid=None):
        data = request.get_json(force=True)
        name = data.get('name')
        buffer = data.get('buffer')
        try:
            distance = layer.get_distances(fid, buffer=buffer)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({"distance": distance})
    return post(lid=lid, fid=fid)
