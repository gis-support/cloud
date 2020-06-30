import binascii
import zipfile
from base64 import b64decode
from datetime import datetime
from mimetypes import guess_type
from tempfile import NamedTemporaryFile
from typing import List, Union, IO

from flask import Blueprint, request, current_app, jsonify, send_file, send_from_directory

from app.blueprints.attachments.models import Attachment
from app.blueprints.layers.layers_attachments import LayerAttachmentsManager, LayerNotSupportedError
from app.db.general import token_required

from app.docs.utils import swag_from_docs
from app.helpers.layer import Layer

mod_attachments_qgis = Blueprint("attachments_qgis", __name__)


@mod_attachments_qgis.route("/attachments_qgis", methods=["POST"])
@swag_from_docs("attachments.post.yml", methods=['POST'])
@token_required
def attachments_post():

    added_at = datetime.now()
    result = []

    payload = request.get_json(force=True)

    layer_id = request.args.get("layer_id")
    feature_id = request.args.get("feature_id")

    files = payload["data"]

    with current_app._db.atomic():
        for file_ in files:
            name = file_["name"]
            content = file_["content"]

            try:
                content = b64decode(content.encode())
            except binascii.Error:
                return jsonify({"error": f"error decoding content of file '{name}'"}), 400

            created = Attachment.create_attachment(name, content, request.user, added_at)
            result.append({
                "original_file_name": name,
                "saved_as": created.file_name,
                "attachment_id": created.id
            })

        if (layer_id is not None) and (feature_id is not None):

            layer = Layer({"app": current_app, "user": request.user, "lid": layer_id})
            try:
                layer.check_write()
            except PermissionError as e:
                return jsonify({"error": str(e)}), 403
            try:
                manager = LayerAttachmentsManager.from_layer(layer)
            except LayerNotSupportedError as e:
                return jsonify({"error": str(e)}), 400

            for row in result:
                manager.add_attachment_to_object(feature_id, row["attachment_id"])

    return jsonify({"data": result}), 201


@mod_attachments_qgis.route("/attachments_qgis/metadata", methods=["GET"])
@swag_from_docs("attachments.metadata.get.yml", methods=['GET'])
@token_required
def attachments_metadata_get():

    ids = request.args.get("ids")

    if (ids is not None) and (ids != ""):
        ids = ids.split(",")
    else:
        ids = []

    layer_id = request.args.get("layer_id")
    feature_id = request.args.get("feature_id")

    query = Attachment.select()
    if len(ids) > 0:
        query = query.where(Attachment.id.in_(ids))

    if (layer_id is not None) and (feature_id is not None):

        layer = Layer({"app": current_app, "user": request.user, "lid": layer_id})
        try:
            manager = LayerAttachmentsManager.from_layer(layer)
        except LayerNotSupportedError as e:
            return jsonify({"error": str(e)}), 400

        attachments_ids = manager.get_attachments_ids_of_object(feature_id)
        query = query.where(Attachment.id.in_(attachments_ids))

    result = list(query.dicts())
    return jsonify({"data": result})


@mod_attachments_qgis.route("/attachments_qgis/files", methods=["GET"])
@swag_from_docs("attachments.files.get.yml", methods=['GET'])
@token_required
def attachments_files_get():

    ids = request.args.get("ids", "")
    ids = ids.split(",")

    if len(ids) == 0 or ids == [""]:
        return jsonify({"error": "at least one ID is required"}), 400

    elif len(ids) == 1:
        id_ = ids[0]

        if (attachment := Attachment.get_or_none(id=id_)) is None:
            return jsonify({"error": f"attachment of ID '{id_}' does not exist"}), 404

        file_content = attachment.get_file_content()
        result_file = NamedTemporaryFile("wb")
        result_file.write(file_content)
        mimetype = guess_type(attachment.file_name)[0] or "application/octet-stream"

        return send_file(result_file.name, mimetype, True, attachment.file_name)

    else:
        query = Attachment.select().where(Attachment.id.in_(ids))
        result_file = get_attachments_as_zip(list(query))

        return send_file(result_file.name, "archive/zip", True, "attachments.zip")


@mod_attachments_qgis.route("/attachments_qgis", methods=["DELETE"])
@swag_from_docs("attachments.delete.yml", methods=['DELETE'])
@token_required
def attachments_delete():

    ids = request.args.get("ids", "")
    ids = ids.split(",")

    layer_id = request.args.get("layer_id")
    feature_id = request.args.get("feature_id")

    if len(ids) == 0 or ids == [""]:
        return jsonify({"error": "at least one ID is required"}), 400

    attachments = Attachment.select().where(Attachment.id.in_(ids))

    with current_app._db.atomic():
        for a in attachments:
            a.delete_instance()

    if (layer_id is not None) and (feature_id is not None):

        layer = Layer({"app": current_app, "user": request.user, "lid": layer_id})
        try:
            layer.check_write()
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403
        try:
            manager = LayerAttachmentsManager.from_layer(layer)
        except LayerNotSupportedError as e:
            return jsonify({"error": str(e)}), 400

        for a in attachments:
            manager.remove_attachment_from_object(feature_id, a.id)

    return jsonify({}), 204


def get_attachments_as_zip(attachments: List[Attachment]) -> Union[IO[bytes], IO]:
    result_file = NamedTemporaryFile("wb")

    archive = zipfile.ZipFile(result_file, mode="w")

    for attachment in attachments:
        archive.writestr(attachment.file_name, attachment.get_file_content())

    archive.close()
    return result_file
