import json
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
from zipfile import ZipFile

import pytest
from flask import Response
from flask.testing import FlaskClient
from freezegun import freeze_time
from werkzeug.http import http_date

from app.blueprints.attachments.models import Attachment
from app.tests.utils import BaseTest


@pytest.mark.attachments_qgis
class TestAttachmentModel:

    @staticmethod
    def create_attachment(file_name: str = "name", data: bytes = b"", added_by: str = "test", added_at: datetime = None):
        added_at = added_at or datetime.now()

        result_file_name = Attachment.create_attachment(file_name, data, added_by, added_at)
        return result_file_name

    def test_create_attachment(self, app_request_context):
        file_name = "attachment.txt"
        data = b"attachment content"
        added_by = "test"
        added_at = datetime.now()

        result = self.create_attachment(file_name, data, added_by, added_at)

        assert isinstance(result, Attachment)
        assert result.file_name == file_name
        assert result.added_by == added_by
        assert result.added_at == added_at

    def test_create_attachment_repeated_name(self, app_request_context):
        file_name = "attachment.txt"
        data = b"attachment content"

        result_1 = self.create_attachment(file_name, data)
        assert result_1.file_name == file_name

        result_2 = self.create_attachment(file_name, data)
        assert result_2.file_name == "attachment_1.txt"

        result_3 = self.create_attachment(file_name, data)
        assert result_3.file_name == "attachment_2.txt"

    def test_create_attachment_and_get_file_content(self, app_request_context):
        file_name = "attachment.txt"
        data = b"attachment content"

        result = self.create_attachment(file_name, data)

        assert result.get_file_content() == data

    def test_create_attachment_and_open_file(self, client: FlaskClient):
        file_name = "attachment.txt"
        data = b"attachment content"

        result = self.create_attachment(file_name, data)

        expected_path = Path(client.application.config["UPLOADS"], "attachments", file_name)
        actual_path = result.get_file_path()
        assert actual_path.exists()
        assert expected_path == actual_path

        expected_file_content = data
        actual_file_content = open(actual_path, "rb").read()
        assert expected_file_content == actual_file_content

    def test_create_attachment_and_open_file_repeated_name(self, client: FlaskClient):
        file_name = "attachment.txt"
        data_1 = b"attachment content"
        data_2 = b"attachment 2 content"

        self.create_attachment(file_name, data_1)
        result_2 = self.create_attachment(file_name, data_2)

        expected_path = Path(client.application.config["UPLOADS"], "attachments", "attachment_1.txt")
        actual_path = result_2.get_file_path()
        assert actual_path.exists()
        assert expected_path == actual_path

        expected_file_content = data_2
        actual_file_content = open(actual_path, "rb").read()
        assert expected_file_content == actual_file_content

    @freeze_time("2020-01-01T10:00:00")
    def test_create_attachment_default_added_at(self, app_request_context):
        result = self.create_attachment()
        assert result.added_at == datetime.fromisoformat("2020-01-01T10:00:00")

    def test_delete_attachment_check_file(self, app_request_context):
        result = self.create_attachment()
        file_path = result.get_file_path()
        result.delete_instance()

        assert file_path.exists() is False


@pytest.mark.attachments_qgis
class TestAttachmentRoutings(BaseTest):

    def create_attachments(self, client: FlaskClient, file_paths: List[Path], token: str) -> Response:
        files = []
        query_string = {"token": token}

        path: Path
        for path in file_paths:
            file_name = path.parts[-1]
            content = path.read_bytes()
            content = b64encode(content)

            files.append({
                "content": content.decode(),
                "name": file_name
            })

        data = {"data": files}
        result = client.post("/api/attachments_qgis", data=json.dumps(data), content_type="multipart/form-data", query_string=query_string)
        return result

    def get_attachments_metadata(self, client: FlaskClient, token: str, ids: List[int] = []) -> Response:
        ids_param = ",".join(map(str, ids))
        query_string = {"token": token, "ids": ids_param}

        result = client.get("/api/attachments_qgis/metadata", query_string=query_string)
        return result

    def get_attachments_files(self, client: FlaskClient, ids: List[int], token: str) -> Response:
        ids_param = ",".join(map(str, ids))
        query_string = {"token": token, "ids": ids_param}

        result = client.get("/api/attachments_qgis/files", query_string=query_string)
        return result

    def delete_attachments(self, client: FlaskClient, ids: List[int], token: str) -> Response:
        ids_param = ",".join(map(str, ids))
        query_string = {"token": token, "ids": ids_param}

        result = client.delete("/api/attachments_qgis", query_string=query_string)
        return result

    def test_create_attachment(self, client: FlaskClient, resources_directory: Path):
        token = self.get_token(client)

        file = Path(resources_directory, "images", "logo.png")

        result = self.create_attachments(client, [file], token)

        assert result.status_code == 201

        actual_data = result.json["data"]

        assert len(actual_data) == 1
        assert actual_data[0]["original_file_name"] == "logo.png"
        assert actual_data[0]["saved_as"] == "logo.png"

    def test_create_attachments_with_same_name(self, client: FlaskClient, resources_directory: Path):
        token = self.get_token(client)

        file_1 = Path(resources_directory, "images", "logo.png")
        file_2 = Path(resources_directory, "images", "logo.png")

        result = self.create_attachments(client, [file_1, file_2], token)

        assert result.status_code == 201

        actual_data = result.json["data"]
        assert len(actual_data) == 2

        actual_data_file_1 = actual_data[0]
        assert actual_data_file_1["original_file_name"] == "logo.png"
        assert actual_data_file_1["saved_as"] == "logo.png"

        actual_data_file_2 = actual_data[1]
        assert actual_data_file_2["original_file_name"] == "logo.png"
        assert actual_data_file_2["saved_as"] == "logo_1.png"

    def test_get_metadata(self, client: FlaskClient):
        token = self.get_token(client)

        result = self.get_attachments_metadata(client, token)
        assert result.status_code == 200
        assert result.json["data"] == []

    @freeze_time("2020-01-01T10:00:00")
    def test_create_and_get_metadata(self, client: FlaskClient, resources_directory: Path):
        token = self.get_token(client, user="admin", password="admin")

        file = Path(resources_directory, "images", "logo.png")
        attachment_id = self.create_attachments(client, [file], token).json["data"][0]["attachment_id"]

        result = self.get_attachments_metadata(client, token, [attachment_id])

        assert result.status_code == 200

        expected_data = [
            {
                "added_by": "admin",
                "id": attachment_id,
                "file_name": "logo.png",
                "added_at": http_date(datetime.fromisoformat("2020-01-01T10:00:00"))
            }
        ]

        assert result.json["data"] == expected_data

    def test_download_empty(self, client: FlaskClient):
        token = self.get_token(client)

        result = self.get_attachments_files(client, [], token)
        assert result.status_code == 400
        assert result.json["error"] == "at least one ID is required"

    def test_download_nonexistent(self, client: FlaskClient):
        token = self.get_token(client)

        result = self.get_attachments_files(client, [0], token)
        assert result.status_code == 404
        assert result.json["error"] == "attachment of ID '0' does not exist"

    def test_create_single_and_download(self, client: FlaskClient, resources_directory: Path):
        token = self.get_token(client)

        file = Path(resources_directory, "images", "logo.png")
        attachment_id = self.create_attachments(client, [file], token).json["data"][0]["attachment_id"]

        result = self.get_attachments_files(client, [attachment_id], token)
        assert result.status_code == 200
        assert result.data == file.read_bytes()

    def test_create_many_and_download_zip(self, client: FlaskClient, resources_directory: Path):
        token = self.get_token(client)

        file_1 = Path(resources_directory, "images", "logo.png")
        attachment_1_id = self.create_attachments(client, [file_1], token).json["data"][0]["attachment_id"]

        file_2 = Path(resources_directory, "images", "logo.png")
        attachment_2_id = self.create_attachments(client, [file_2], token).json["data"][0]["attachment_id"]

        result = self.get_attachments_files(client, [attachment_1_id, attachment_2_id], token)
        assert result.status_code == 200

        zip_path = NamedTemporaryFile()
        archive = ZipFile(zip_path, mode="w")
        archive.writestr("logo.png", file_1.read_bytes())
        archive.writestr("logo_1.png", file_2.read_bytes())
        archive.close()

        expected_data = Path(zip_path.name).read_bytes()

        assert result.headers["Content-Disposition"] == "attachment; filename=attachments.zip"
        assert result.headers["Content-Type"] == "archive/zip"
        assert result.get_data() == expected_data

    def test_delete_empty(self, client: FlaskClient):
        token = self.get_token(client)

        result = self.delete_attachments(client, [], token)
        assert result.status_code == 400
        assert result.json["error"] == "at least one ID is required"

    def test_create_and_delete(self, client: FlaskClient, resources_directory: Path):
        token = self.get_token(client)

        file = Path(resources_directory, "images", "logo.png")
        attachment_id = self.create_attachments(client, [file], token).json["data"][0]["attachment_id"]

        result = self.delete_attachments(client, [attachment_id], token)
        assert result.status_code == 204
