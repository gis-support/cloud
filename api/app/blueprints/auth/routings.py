#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app
from flasgger import swag_from
from app.docs import path_by
from app.db.general import user_exists, create_user, authenticate_user, create_token


mod_auth = Blueprint("auth", __name__)


@mod_auth.route('/register', methods=['POST'])
@swag_from(path_by(__file__, 'docs.register.post.yml'), methods=['POST'])
def register():
    payload = request.get_json(force=True)
    user = payload.get("user")
    if not user:
        return jsonify({"error": "user required"}), 400
    password = payload.get("password")
    if not user:
        return jsonify({"error": "password required"}), 400
    if user_exists(user):
        return jsonify({"error": "user exists"}), 409
    create_user(user, password)
    return jsonify({"register": "user created"}), 201


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
