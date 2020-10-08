#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, send_file
from flasgger import swag_from

from app.blueprints.layers.utils import ATTACHMENTS_COLUMN_NAME
from app.blueprints.rdos.analysis.distance_analysis import get_xlsx, get_xlsx_geojson
from app.blueprints.rdos.analysis.intersection_analysis import get_intersecting_features_ids
from app.docs import path_by
from app.db.general import token_required, layer_decorator, admin_only
from app.helpers.layer import get_features_as_xlsx
from app.helpers.cloud import cloud_decorator
from app.blueprints.rdos.analysis.models import Settings

import json

mod_analysis = Blueprint("analysis", __name__)


@mod_analysis.route('/analysis/settings', methods=['GET', 'PUT'])
@swag_from(path_by(__file__, 'docs.settings.get.yml'), methods=['GET'])
@swag_from(path_by(__file__, 'docs.settings.put.yml'), methods=['PUT'])
@token_required
def settings():
    if request.method == 'GET':
        return jsonify({"settings": Settings.get_settings()})

    elif request.method == 'PUT':
        @admin_only
        def put():
            Settings.update_settings(request.get_json(force=True))
            return jsonify({"settings": Settings.get_settings()})
        return put()


@mod_analysis.route('/analysis/distance/<lid>/<int:fid>', methods=['POST'])
@swag_from(path_by(__file__, 'docs.distance.post.yml'), methods=['POST'])
@token_required
def analysis_distance(lid, fid):

    @layer_decorator(permission="read")
    def post(layer, lid=None, fid=None):
        data = request.get_json(force=True)
        name = data.get('name')
        buffer = data.get('buffer')
        try:
            distance = layer.get_distances(fid, buffer=buffer)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify({"distance": distance})
    return post(lid=lid, fid=fid)


@mod_analysis.route('/analysis/distance/<lid>/<int:fid>/xlsx', methods=['POST'])
@swag_from(path_by(__file__, 'docs.distance.xlsx.post.yml'), methods=['POST'])
@token_required
def analysis_distance_xlsx(lid, fid):

    @layer_decorator(permission="read")
    def post(layer, lid=None, fid=None):
        data = request.get_json(force=True)
        name_attribute = data.get('name')
        buffer_distance = data.get('buffer')
        feature = layer.as_geojson_by_fid(fid)
        feature_properties = feature["properties"]
        if name_attribute not in feature_properties.keys():
            return jsonify({"error": f"column '{name_attribute}' does not exist"})

        feature_name = feature_properties[name_attribute]

        try:
            file = get_xlsx(layer, fid, buffer_distance, feature_name)

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403

        file_name = f"{feature_name} ({layer.name}) - analiza odległości.xlsx"
        return send_file(file.name, as_attachment=True, attachment_filename=file_name)

    return post(lid=lid, fid=fid)

@mod_analysis.route('/analysis/distance/xlsx', methods=['POST'])
@swag_from(path_by(__file__, 'docs.distance.xlsx.geojson.post.yml'), methods=['POST'])
@token_required
@cloud_decorator
def analysis_distance_xlsx_geojson(cloud):
    data = request.get_json(force=True)
    try:
        teryt = data['properties']['teryt']
        buffer = data['properties']['buffer']
        geometry = json.dumps(data['geometry'])
    except:
        return jsonify({"error": "invalid geojson"}), 400
    try:
        file_xlsx = get_xlsx_geojson(cloud, geometry, buffer, teryt)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    file_name = f"Analiza odległości dla działki {teryt}.xlsx"
    return send_file(file_xlsx.name, as_attachment=True, attachment_filename=file_name)

@mod_analysis.route("/analysis/intersection/<lid>", methods=["POST"])
@swag_from(path_by(__file__, 'docs.analysis.intersection.post.yml'), methods=['POST'])
@token_required
def analysis_buffer(lid):
    @layer_decorator(permission="read")
    def post(layer, lid=None, fid=None):
        data = request.get_json(force=True)
        geometry = data["geometry"]

        response_type = request.args.get("response_type")
        if response_type not in ("xlsx", "json"):
            response_type = "json"

        ids = get_intersecting_features_ids(layer, geometry, 4326)

        if response_type == "xlsx":
            file = get_features_as_xlsx(layer, ids)
            return send_file(file.name, as_attachment=True, attachment_filename="obiekty.xlsx")

        else:
            features = layer.get_features(ids)
            result = []
            for feature in features:
                feature.pop("geometry")
                feature.pop(ATTACHMENTS_COLUMN_NAME)
                result.append(feature)

            return jsonify({"data": result})

    return post(lid=lid)
