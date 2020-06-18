from datetime import datetime
from pathlib import Path

import pytest
from flask.testing import FlaskClient
from freezegun import freeze_time

from app.blueprints.attachments.models import Attachment


@pytest.mark.attachments_qgis
class TestAttachmentModel:

    @staticmethod
    def create_attachment(file_name: str, data: bytes, added_by: str = "test", added_at: datetime = None):
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

    def test_create_attachment_and_get_file_data(self, app_request_context):
        file_name = "attachment.txt"
        data = b"attachment content"

        result = self.create_attachment(file_name, data)

        assert result.get_file_data() == data

    def test_create_attachment_and_open_file(self, client: FlaskClient):
        file_name = "attachment.txt"
        data = b"attachment content"

        result = self.create_attachment(file_name, data)

        expected_path = Path(client.application.config["UPLOADS"], "attachments", file_name)
        actual_path = result.get_file_path()
        assert actual_path.exists()
        assert expected_path == actual_path

        expected_file_data = data
        actual_file_data = open(actual_path, "rb").read()
        assert expected_file_data == actual_file_data

    def test_create_attachment_and_open_file_repeated_name(self, client: FlaskClient):
        file_name = "attachment.txt"
        data = b"attachment content"

        self.create_attachment(file_name, data)
        result_2 = self.create_attachment(file_name, data)

        expected_path = Path(client.application.config["UPLOADS"], "attachments", "attachment_1.txt")
        actual_path = result_2.get_file_path()
        assert actual_path.exists()
        assert expected_path == actual_path

        expected_file_data = data
        actual_file_data = open(actual_path, "rb").read()
        assert expected_file_data == actual_file_data

    @freeze_time("2020-01-01T10:00:00")
    def test_create_attachment_default_added_at(self, app_request_context):
        file_name = "attachment.txt"
        data = b"attachment content"

        result = self.create_attachment(file_name, data)
        assert result.added_at == datetime.fromisoformat("2020-01-01T10:00:00")

    def test_delete_attachment_check_file(self, app_request_context):
        file_name = "attachment.txt"
        data = b"attachment content"

        result = self.create_attachment(file_name, data)
        file_path = result.get_file_path()
        result.delete_instance()

        assert file_path.exists() is False
