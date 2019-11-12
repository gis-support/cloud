#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, current_app
from app.docs import swagger
from app.db.general import user_exists, create_user, authenticate_user, create_token

mod_auth = Blueprint("auth", __name__)

@mod_auth.route('/register', methods=['POST'])
@swagger(__file__, 'docs.register.post.yml')
def register():
    payload = request.get_json(force=True)
    if user_exists(payload['user']):
        return jsonify({"error": "user exists"}), 409
    create_user(payload['user'], payload['password'])
    return jsonify({"register": "user created"}), 201

@mod_auth.route('/login', methods=['POST'])
@swagger(__file__, 'docs.login.post.yml')
def login():
    payload = request.get_json(force=True)
    if not authenticate_user(payload['user'], payload['password']):
        return jsonify({"error": "invalid credentials"}), 403
    token = create_token(payload['user'])
    return jsonify({"token": token})