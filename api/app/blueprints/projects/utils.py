from flask import current_app

from app.blueprints.projects.models import Project
from app.helpers.layer import Layer


def does_user_have_permission_to_active_layer(user_name: str, project: Project) -> bool:
    layer_id = project.active_layer_id

    try:
        Layer(
            {"app": current_app, "user": user_name, "lid": layer_id})
    except PermissionError:
        return False

    return True


def does_user_have_permission_to_each_additional_layer(user_name: str, project: Project) -> bool:
    layers_ids = project.additional_layers_ids

    for layer_id in layers_ids:
        try:
            Layer(
                {"app": current_app, "user": user_name, "lid": layer_id})
        except PermissionError:
            return False

    return True


