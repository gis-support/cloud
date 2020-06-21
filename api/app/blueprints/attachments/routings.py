import binascii
import zipfile
from base64 import b64decode
from datetime import datetime
from mimetypes import guess_type
from tempfile import NamedTemporaryFile
from typing import List, Union, IO

from flask import Blueprint, request, current_app, jsonify, send_file

from app.blueprints.attachments.models import Attachment
from app.db.general import token_required

from app.docs.utils import swag_from_docs


mod_attachments_qgis = Blueprint("attachments_qgis", __name__)


@mod_attachments_qgis.route("/attachments_qgis", methods=["POST"])
@swag_from_docs("attachments.post.yml", methods=['POST'])
@token_required
def attachments_post():

    added_at = datetime.now()
    result = []

    payload = request.get_json(force=True)

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

    query = Attachment.select()
    if len(ids) > 0:
        query = query.where(Attachment.id.in_(ids))

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
        attachments = Attachment.select().where(Attachment.id.in_(ids))
        result_file = get_attachments_as_zip(attachments)

        return send_file(result_file.name, "archive/zip", True, "attachments.zip")


@mod_attachments_qgis.route("/attachments_qgis", methods=["DELETE"])
@swag_from_docs("attachments.delete.yml", methods=['DELETE'])
@token_required
def attachments_delete():

    ids = request.args.get("ids", "")
    ids = ids.split(",")

    if len(ids) == 0 or ids == [""]:
        return jsonify({"error": "at least one ID is required"}), 400

    attachments = Attachment.select().where(Attachment.id.in_(ids))

    with current_app._db.atomic():
        for a in attachments:
            a.delete_instance()

    return jsonify({}), 204


def get_attachments_as_zip(attachments: List[Attachment]) -> Union[IO[bytes], IO]:
    result_file = NamedTemporaryFile("wb")

    archive = zipfile.ZipFile(result_file, mode="w")

    for attachment in attachments:
        archive.writestr(attachment.file_name, attachment.get_file_content())

    archive.close()
    return result_file
