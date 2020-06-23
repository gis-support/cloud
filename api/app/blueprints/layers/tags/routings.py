import os

from flasgger import swag_from
from flask import jsonify, request

from app.blueprints.layers.routings import mod_layers
from app.blueprints.layers.tags.models import LayerTag, Tag
from app.db.general import token_required
from app.docs import path_by


@mod_layers.route("/tags")
@swag_from(path_by(__file__, 'docs/tags.get.yml'), methods=['GET'])
@token_required
def tags_get():
    query = Tag.select()
    result = list(query.dicts())

    return jsonify({"data": result})

@mod_layers.route("/tags", methods=["POST"])
@swag_from(path_by(__file__, 'docs/tags.post.yml'), methods=['POST'])
@token_required
def tags_post():
    payload = request.get_json(force=True)
    required_attributes = ("name", "color")

    if set(payload.keys()) != set(required_attributes):
        return jsonify({"error": "invalid attributes - {} are required".format(required_attributes)}), 400

    name = payload["name"]

    if Tag.does_tag_with_name_exist(name):
        return jsonify({"error": f"tag with name '{name}' already exists"}), 400

    tag = Tag(name=name, color=payload["color"])
    tag.save()

    return jsonify({"data": tag.id}), 201

@mod_layers.route("/tags/<int:tag_id>", methods=["PUT", "DELETE"])
@swag_from(path_by(__file__, 'docs/tags.tag_id.put.yml'), methods=["PUT"])
@swag_from(path_by(__file__, 'docs/tags.tag_id.delete.yml'), methods=["DELETE"])
@token_required
def tags_tag_id_delete(tag_id: int):
    tag = Tag.get_or_none(id=tag_id)

    if tag is None:
        return jsonify({"error": f"tag with ID '{tag_id}' does not exist"}), 404

    if request.method == "PUT":
        payload = request.get_json(force=True)
        name = payload["name"]

        if Tag.select().where(Tag.name == name, Tag.id != tag_id).exists():
            return jsonify({"error": f"tag with name '{name}' already exists"}), 400
        Tag.update(**payload).where(Tag.id == tag_id).execute()

    if request.method == "DELETE":
        tag.delete_instance(recursive=True)

    return jsonify({}), 204

@mod_layers.route("/tags/layers", methods=["POST", "DELETE"])
@swag_from(path_by(__file__, 'docs/tags.layers.post.yml'), methods=['POST'])
@swag_from(path_by(__file__, 'docs/tags.layers.delete.yml'), methods=['DELETE'])
@token_required
def layers_tag_post_delete():
    required_args = {"layer_id", "tag_id"}

    missing_args = required_args - set(request.args.keys())
    if len(missing_args) > 0:
        return jsonify({"error": f"missing arguments: {missing_args}"}), 400

    layer_id = request.args["layer_id"]
    tag_id = request.args["tag_id"]

    layer_tag = LayerTag.get_or_none(layer_id=layer_id, tag=tag_id)

    if Tag.get_or_none(id=tag_id) is None:
        return jsonify({"error": f"tag with ID '{tag_id}' does not exist"}), 400

    if request.method == "POST":
        if layer_tag is not None:
            return jsonify({"error": f"layer '{layer_id}' already tagged with tag '{tag_id}'"}), 400

        layer_tag = LayerTag(layer_id=layer_id, tag=tag_id)
        layer_tag.save()
    else:
        if layer_tag is None:
            return jsonify({"error": f"layer '{layer_id}' is not tagged with tag '{tag_id}'"}), 400

        layer_tag.delete_instance()

    return jsonify({}), 204
