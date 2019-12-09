#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.docs import path_by
from app.db.general import token_required, layer_decorator
from app.helpers.layer import Layer
from app.blueprints.rdos.attachments.models import Attachment

mod_attachments = Blueprint("attachments", __name__)


@mod_attachments.route('/layers/<lid>/attachments', methods=['GET'])
@swag_from(path_by(__file__, 'docs.attachments.get.yml'), methods=['GET'])
@token_required
@layer_decorator(permission="read")
def attachments(layer, lid):
    return jsonify({"attachments": Attachment.get_all_for_group(layer.get_user_group())})
