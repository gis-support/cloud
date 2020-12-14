#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.db.general import token_required, layer_decorator, user_exists, admin_only
from app.helpers.cloud import PERMISSIONS
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
    return jsonify(cloud.get_permissions(grantor=is_admin(request.user)))


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


@mod_permissions.route('/permissions/copy', methods=['POST'])
@swag_from(path_by(__file__, 'docs.permissions.copy.post.yml'), methods=['POST'])
@token_required
@admin_only
@cloud_decorator
def permissions_copy(cloud):
    data = request.get_json(force=True)
    user_from = data.get("user_from")
    user_to = data.get("user_to")

    if not user_exists(user_from):
        return jsonify({"error": "user_from not exists"}), 400
    if not user_exists(user_to):
        return jsonify({"error": "user_to not exists"}), 400
    if is_admin(user_to):
        return jsonify({"error": "administrator permissions can not be changed"}), 400

    permissions = cloud.copy_permissions(user_from, user_to)

    return jsonify({"user": user_to, "permissions": permissions})
