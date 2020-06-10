#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.docs import path_by
from app.db.general import token_required
from app.helpers.cloud import cloud_decorator
from app.blueprints.rdos.services.models import Service
import os

mod_services = Blueprint("services", __name__)


@mod_services.route('/services/<sid>', methods=['DELETE'])
@swag_from(path_by(__file__, 'docs.services.delete.yml'), methods=['DELETE'])
@token_required
@cloud_decorator
def service_delete(cloud, sid):
    if request.method == 'DELETE':
        """
        Delete service
        Returns service id
        """
        def delete(sid=sid):
            error, code = Service.check_permission(sid, cloud.get_user_group())
            if error:
                return jsonify({"error": error}), code
            return jsonify({"sid": Service.delete_service(sid)})
        return delete(sid=sid)


@mod_services.route('/services', methods=['GET', 'POST'])
@swag_from(path_by(__file__, 'docs.services.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.services.post.yml'), methods=['POST'])
@token_required
@cloud_decorator
def services(cloud):
    if request.method == 'GET':
        """
        Get map services
        Returns services list
        """
        def get():
            return jsonify({"services": Service.get_services(cloud.get_user_group())})
        return get()

    elif request.method == 'POST':
        """
        Add map service
        Returns service
        """
        def post():
            data = request.get_json(force=True)
            if 'public' in data and data['public'] == False:
                data['group'] = cloud.get_user_group()
            else:
                data['group'] = os.environ['DEFAULT_GROUP']
            error, code = Service.validate(data)
            if error:
                return jsonify({"error": error}), code
            service = Service.add_service(data)
            return jsonify({"services": service}), 201
        return post()
