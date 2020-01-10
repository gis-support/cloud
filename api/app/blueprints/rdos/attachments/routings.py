#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.docs import path_by
from app.db.general import token_required, layer_decorator
from app.helpers.layer import Layer
from app.blueprints.rdos.attachments.models import Attachment

mod_attachments = Blueprint("attachments", __name__)


@mod_attachments.route('/layers/<lid>/features/<int:fid>/attachments/<int:aid>', methods=['DELETE'])
@swag_from(path_by(__file__, 'docs.attachments.delete.yml'), methods=['DELETE'])
@token_required
def attachment_delete(lid, fid, aid):
    if request.method == 'DELETE':
        """
        Delete attachment for feature
        Returns attachments list
        """
        @layer_decorator(permission="owner")
        def delete(layer, lid=lid, fid=fid, aid=None):
            return jsonify({"aid": Attachment.delete_attachment(lid, fid, aid)})
        return delete(lid=lid, fid=fid, aid=aid)


@mod_attachments.route('/layers/<lid>/features/<int:fid>/attachments', methods=['GET', 'POST'])
@swag_from(path_by(__file__, 'docs.attachments.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.attachments.post.yml'), methods=['POST'])
@token_required
def attachments(lid, fid):
    if request.method == 'GET':
        """
        Get attachments for feature
        Returns attachments list
        """
        @layer_decorator(permission="write")
        def get(layer, lid=None, fid=None):
            return jsonify({"attachments": Attachment.get_attachments(lid=lid, fid=fid, group='default')})
        return get(lid=lid, fid=fid)

    elif request.method == 'POST':
        """
        Add attachment to feature
        Returns confirmation
        """
        @layer_decorator(permission="write")
        def post(layer, lid=None, fid=None):
            data = request.get_json(force=True)
            model = {
                'lid': lid,
                'fid': fid,
                # Domyślnie dodawany załącznik jest publiczny
                'group': 'public' if data.get('public', True) else layer.get_user_group(),
                # Domyślny link do GIS Support
                'link': data.get('link', 'https://gis-support.pl/'),
                # Domyślna nazwa załącznika to null
                'name': data.get('name', None)
            }
            attachment = Attachment.add_attachment(model)
            return jsonify({"attachments": attachment}), 201
        return post(lid=lid, fid=fid)
