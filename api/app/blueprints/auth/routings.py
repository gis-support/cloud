#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app
from flasgger import swag_from
from app.docs import path_by
from app.db.general import user_exists, create_user, authenticate_user, create_token, token_required, cloud_decorator


mod_auth = Blueprint("auth", __name__)


@mod_auth.route('/login', methods=['POST'])
@swag_from(path_by(__file__, 'docs.login.post.yml'), methods=['POST'])
def login():
    payload = request.get_json(force=True)
    user = payload.get("user")
    if not user:
        return jsonify({"error": "user required"}), 400
    password = payload.get("password")
    if not password:
        return jsonify({"error": "password required"}), 400
    if not authenticate_user(user, password):
        return jsonify({"error": "invalid credentials"}), 403
    token = create_token(user)
    return jsonify({"token": token})


@mod_auth.route('/check_token', methods=['GET'])
@swag_from(path_by(__file__, 'docs.checktoken.get.yml'), methods=['GET'])
@token_required
def check_token():
    return jsonify({"token": "valid"})


@mod_auth.route('/users', methods=['POST', 'PUT'])
@swag_from(path_by(__file__, 'docs.users.post.yml'), methods=['POST'])
@swag_from(path_by(__file__, 'docs.users.put.yml'), methods=['PUT'])
@token_required
@cloud_decorator
def users(cloud):
    payload = request.get_json(force=True)
    user = payload.get("user")
    if not user:
        return jsonify({"error": "user required"}), 400
    if request.method == 'POST':
        if user_exists(user):
            return jsonify({"error": "user exists"}), 409
        password = payload.get("password")
        if not user:
            return jsonify({"error": "password required"}), 400
        group = payload.get("group", current_app.config['DEFAULT_GROUP'])
        create_user(user, password, group)
        return jsonify({"users": "user created"}), 201
    elif request.method == 'PUT':
        if not user_exists(user):
            return jsonify({"error": "user not exists"}), 409
        group = payload.get("group")
        if not cloud.group_exists(group):
            return jsonify({"error": "group not exists"}), 409
        cloud.assign_user(user, group)
        return jsonify({"users": "user assigned"}), 200


@mod_auth.route('/users/groups', methods=['GET', 'POST', 'DELETE'])
@swag_from(path_by(__file__, 'docs.groups.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.groups.post.yml'), methods=['POST'])
@swag_from(path_by(__file__, 'docs.groups.delete.yml'), methods=['DELETE'])
@token_required
@cloud_decorator
def groups(cloud):
    if request.method == 'GET':
        return jsonify({"groups": cloud.get_groups()})
    elif request.method == 'POST':
        payload = request.get_json(force=True)
        group = payload.get('group')
        if not group:
            return jsonify({"error": "group name required"}), 400
        try:
            cloud.add_group(group)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({"groups": "group added"}), 201
    elif request.method == 'DELETE':
        payload = request.get_json(force=True)
        group = payload.get('group')
        if not group:
            return jsonify({"error": "group name required"}), 400
        try:
            cloud.delete_group(group)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({"groups": "group deleted"})
