#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.db.general import token_required, layer_decorator, user_exists, cloud_decorator
from app.helpers.layer import PERMISSIONS
from flasgger import swag_from
from app.docs import path_by

mod_permissions = Blueprint("permissions", __name__)


@mod_permissions.route('/permissions')
@swag_from(path_by(__file__, 'docs.permissions.get.yml'))
@token_required
@cloud_decorator
def permissions(cloud):
    return jsonify({"permissions": cloud.get_permissions()})


@mod_permissions.route('/permissions/<lid>', methods=['PUT'])
@swag_from(path_by(__file__, 'docs.permissions.id.put.yml'), methods=['PUT'])
@token_required
@layer_decorator(permission="owner")
def permissions_by_layer_id(layer, lid):
    data = request.get_json(force=True)
    if data.get('permission') not in PERMISSIONS:
        return jsonify({"error": "permission invalid"}), 400
    if not user_exists(data.get('user')):
        return jsonify({"error": "user not exists"}), 400
    layer.grant(user=data['user'], permission=data['permission'])
    return jsonify({"permissions": {"user": data['user'], "permission": data["permission"]}})