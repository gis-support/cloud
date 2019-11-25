#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app.db.general import token_required, layer_decorator, user_exists
from app.helpers.layer import PERMISSIONS

mod_permissions = Blueprint("permissions", __name__)


@mod_permissions.route('/permissions/<lid>', methods=['PUT'])
@token_required
@layer_decorator(permission="owner")
def permissions(layer, lid):
    if request.method == 'GET':
        return jsonify({"tests": "test"})
    elif request.method == 'PUT':
        data = request.get_json(force=True)
        if data.get('permission') not in PERMISSIONS:
            return jsonify({"error": "permission invalid"}), 400
        if not user_exists(data.get('user')):
            return jsonify({"error": "user not exists"}), 400
        layer.grant(user=data['user'], permission=data['permission'])
        return jsonify({"permissions": "ok"})
