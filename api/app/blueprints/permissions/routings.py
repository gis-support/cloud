#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.db.general import token_required, layer_decorator, user_exists
from app.helpers.layer import PERMISSIONS
from flasgger import swag_from
from app.docs import path_by
from os import environ
from app.helpers.cloud import cloud_decorator
from app.helpers.users import is_admin

mod_permissions = Blueprint("permissions", __name__)


@mod_permissions.route('/permissions')
@swag_from(path_by(__file__, 'docs.permissions.get.yml'))
@token_required
@cloud_decorator
def permissions(cloud):
    admin = True if request.user == environ.get('DEFAULT_USER') else False
    return jsonify(cloud.get_permissions(grantor=admin))


@mod_permissions.route('/permissions/<lid>', methods=['PUT'])
@swag_from(path_by(__file__, 'docs.permissions.id.put.yml'), methods=['PUT'])
@token_required
@layer_decorator(permission="owner")
def permissions_by_layer_id(layer, lid):
    data = request.get_json(force=True)

    user = data.get("user", "")
    if is_admin(user):
        return jsonify({"error": "administrator permissions can not be changed"}), 400

    if data.get('permission') not in PERMISSIONS:
        return jsonify({"error": "permission invalid"}), 400
    if not user_exists(user):
        return jsonify({"error": "user not exists"}), 400
    layer.grant(user=data['user'], permission=data['permission'])
    return jsonify({"permissions": {"user": data['user'], "permission": data["permission"]}})
