#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flasgger import swag_from
from app.docs import path_by
from app.db.general import user_exists, create_user, authenticate_user, create_token, token_required, delete_user, admin_only
import os
from app.helpers.cloud import cloud_decorator


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


@mod_auth.route('/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
@swag_from(path_by(__file__, 'docs.users.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.users.post.yml'), methods=['POST'])
@swag_from(path_by(__file__, 'docs.users.put.yml'), methods=['PUT'])
@swag_from(path_by(__file__, 'docs.users.delete.yml'), methods=['DELETE'])
@token_required
@admin_only
@cloud_decorator
def users(cloud):
    if request.method == 'GET':
        return jsonify({"users": cloud.get_users_with_groups()})
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
        group = payload.get("group", os.environ['DEFAULT_GROUP'])
        create_user(user, password, group)
        return jsonify({"users": "user created"}), 201
    elif request.method == 'PUT':
        if not user_exists(user):
            return jsonify({"error": "user not exists"}), 409
        group = payload.get("group")
        if not cloud.group_exists(group):
            return jsonify({"error": "group not exists"}), 409
        old_group = cloud.get_user_group(user)
        if old_group != group:
            if old_group != os.environ['DEFAULT_GROUP']:
                cloud.unassign_user(user, old_group)
            cloud.assign_user(user, group)
        return jsonify({"users": "user assigned"}), 200
    elif request.method == 'DELETE':
        admin = os.environ.get('DEFAULT_USER')
        if request.user != admin or user == admin:
            return jsonify({"error": "permission denied"}), 403
        delete_user(user)
        return jsonify({"users": "user deleted"}), 200


@mod_auth.route('/users/groups', methods=['GET', 'POST', 'DELETE'])
@swag_from(path_by(__file__, 'docs.groups.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.groups.post.yml'), methods=['POST'])
@swag_from(path_by(__file__, 'docs.groups.delete.yml'), methods=['DELETE'])
@token_required
@admin_only
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


@mod_auth.route('/logo', methods=['GET'])
@swag_from(path_by(__file__, 'docs.logo.get.yml'), methods=['GET'])
def logo():
    return send_from_directory(current_app.config['STATIC'], 'logo.png')


@mod_auth.route('/logo', methods=['POST'])
@swag_from(path_by(__file__, 'docs.logo.post.yml'), methods=['POST'])
@token_required
def upload_logo():
    f = request.files['file']
    f.save(os.path.join(current_app.config['STATIC'], 'logo.png'))
    return send_from_directory(current_app.config['STATIC'], 'logo.png'), 201


@mod_auth.route('/favicon', methods=['GET'])
@swag_from(path_by(__file__, 'docs.favicon.get.yml'), methods=['GET'])
def get_favicon():
    return send_from_directory(current_app.config['STATIC'], 'favicon.ico')


@mod_auth.route('/favicon', methods=['POST'])
@swag_from(path_by(__file__, 'docs.favicon.post.yml'), methods=['POST'])
@token_required
def upload_favicon():
    f = request.files['file']
    f.save(os.path.join(current_app.config['STATIC'], 'favicon.ico'))
    return send_from_directory(current_app.config['STATIC'], 'favicon.ico'), 201