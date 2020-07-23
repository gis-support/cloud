import json

from flask import Blueprint, request, jsonify, current_app
from peewee import fn
from playhouse.shortcuts import model_to_dict

from app.blueprints.projects.models import Project
from app.blueprints.projects.utils import does_user_have_permission_to_active_layer, \
    does_user_have_permission_to_each_additional_layer
from app.db.general import token_required
from app.docs.utils import swag_from_docs
from app.helpers.layer import Layer
from app.helpers.users import is_admin

mod_projects = Blueprint("projects", __name__)


@mod_projects.route("/projects")
@token_required
@swag_from_docs("projects.get.yml")
def projects_get():
    user_name = request.user
    query = Project.select().where(Project.owner_name == user_name)

    result = []
    for project in query:
        project_dict = model_to_dict(project)

        project_dict["permission_to_each_additional_layer"] = does_user_have_permission_to_each_additional_layer(user_name, project)
        project_dict["permission_to_active_layer"] = does_user_have_permission_to_active_layer(user_name, project)
        project_dict.pop("owner_name")
        result.append(project_dict)

    return jsonify({"data": result})


@mod_projects.route("/projects/<int:project_id>")
@token_required
@swag_from_docs("projects.project_id.get.yml")
def projects_project_id_get(project_id: int):
    user_name = request.user

    project = Project.get_or_none(Project.id == project_id)

    if project is None:
        return jsonify({"error": "project does not exist"}), 404

    if not does_user_have_permission_to_active_layer(user_name, project):
        return jsonify({"error": "permission denied for project`s active layer"}),  403

    result = model_to_dict(project)
    result["permission_to_each_additional_layer"] = does_user_have_permission_to_each_additional_layer(user_name, project)
    result.pop("owner_name")

    return jsonify({"data": result})


@mod_projects.route("/projects", methods=["POST"])
@token_required
@swag_from_docs("projects.post.yml", methods=["POST"])
def projects_post():
    user_name = request.user

    data = request.get_json(force=True)
    data["owner_name"] = user_name

    active_layer_id = data["active_layer_id"]
    additional_layers_ids = data.get('additional_layers_ids', [])

    layers_ids = additional_layers_ids + [active_layer_id]

    for layer_id in layers_ids:
        try:
            Layer(
                {"app": current_app, "user": user_name, "lid": layer_id})
        except ValueError as e:
            return jsonify({"error": f"layer {layer_id} does not exist"}), 400
        except PermissionError as e:
            return jsonify({"error": f"permission denied to layer {layer_id}"}), 403

    map_center = data["map_center"]
    data["map_center"] = fn.ST_GeomFromGeoJSON(json.dumps(map_center))

    project = Project(**data)
    project.save()

    return jsonify({"data": project.id}), 201


@mod_projects.route("/projects/<int:project_id>", methods=["PUT"])
@token_required
@swag_from_docs("projects.project_id.put.yml", methods=["PUT"])
def projects_project_id_put(project_id: int):
    user_name = request.user

    project = Project.get_or_none(Project.id == project_id)

    if project is None:
        return jsonify({"error": "project does not exist"}), 404

    if not is_admin(user_name):
        if project.owner_name != user_name:
            return jsonify({"error": "permission denied to other users projects"}), 403

    data = request.get_json(force=True)

    data.pop("owner_name", None)

    active_layer_id = data.get("active_layer_id")
    additional_layers_ids = data.get('additional_layers_ids', [])

    layers_ids = additional_layers_ids
    if active_layer_id is not None:
        layers_ids.append(active_layer_id)

    for layer_id in layers_ids:
        try:
            Layer(
                {"app": current_app, "user": user_name, "lid": layer_id})
        except ValueError as e:
            return jsonify({"error": f"layer {layer_id} does not exist"}), 400
        except PermissionError as e:
            return jsonify({"error": f"permission denied to layer {layer_id}"}), 403

    map_center = data["map_center"]
    data["map_center"] = fn.ST_GeomFromGeoJSON(json.dumps(map_center))

    Project.update(**data).where(Project.id == project_id).execute()
    return jsonify({}), 204


@mod_projects.route("/projects/<int:project_id>", methods=["DELETE"])
@token_required
@swag_from_docs("projects.project_id.delete.yml", methods=["DELETE"])
def projects_project_id_delete(project_id: int):
    user_name = request.user

    project = Project.get_or_none(Project.id == project_id)

    if project is None:
        return jsonify({"error": "project does not exist"}), 404

    if not is_admin(user_name):
        if project.owner_name != user_name:
            return jsonify({"error": "permission denied to other users projects"}), 403

    project.delete_instance()
    return jsonify({}), 204
