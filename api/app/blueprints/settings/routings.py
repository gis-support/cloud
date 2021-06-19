from app.blueprints.settings.models import Setting
from app.db.general import token_required, admin_only
from app.docs import path_by
from flasgger import swag_from
from flask import Blueprint, request, jsonify

mod_settings = Blueprint('settings', __name__)


@mod_settings.route('/app_name', methods=["GET"])
@swag_from(path_by(__file__, 'docs.app_name.get.yml'), methods=['GET'])
def get_app_name():
    app_name = Setting.get_app_name()
    return jsonify({"app_name": app_name}), 200
    

@mod_settings.route('/app_name', methods=["PUT"])
@swag_from(path_by(__file__, 'docs.app_name.put.yml'), methods=['PUT'])
@token_required
@admin_only
def put_app_name():
    payload = request.get_json(force=True)
    app_name = payload.get("app_name")
    if not app_name:
        return jsonify({"error": "app name is required"}), 400
    message, message_code = Setting.put_app_name(payload)
    return jsonify({"settings": message}), message_code
