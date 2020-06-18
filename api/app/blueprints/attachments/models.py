import os
from datetime import datetime
from pathlib import Path

from flask import current_app
from peewee import AutoField, TextField, DateTimeField

from app.db.base_model import BaseModel

class Attachment(BaseModel):

    class Meta:
        table_name = "attachment_qgis"

    id = AutoField(primary_key=True)
    file_name = TextField(unique=True)
    added_by = TextField()
    added_at = DateTimeField(default=datetime.now)

    @staticmethod
    def _get_attachments_directory_path() -> str:
        return os.path.join(current_app.config["UPLOADS"], "attachments")

    @classmethod
    def _ensure_attachments_directory_exists(cls):
        path = cls._get_attachments_directory_path()
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def _save_file(cls, file_name: str, file_content: bytes):
        file_path = os.path.join(cls._get_attachments_directory_path(), file_name)
        candidate_file_path = file_path
        suffix = 0

        while os.path.exists(candidate_file_path):
            base_name, extension = os.path.splitext(file_path)

            suffix += 1
            candidate_file_path = f"{base_name}_{suffix}{extension}"

        if suffix > 0:
            base_name, extension = os.path.splitext(file_path)
            file_path = f"{base_name}_{suffix}{extension}"

        with open(file_path, "wb") as f:
            f.write(file_content)

        return os.path.split(file_path)[1]

    @classmethod
    def create_attachment(cls, file_name: str, file_content: bytes, added_by: str, added_at: datetime) -> "cls":
        cls._ensure_attachments_directory_exists()

        file_name = cls._save_file(file_name, file_content)

        attachment = Attachment(file_name=file_name, added_at=added_at, added_by=added_by)
        attachment.save()

        return attachment

    def _remove_file(self):
        path = self.get_file_path()
        path.unlink()

    def delete_instance(self, recursive=False, delete_nullable=False):
        result = super().delete_instance(recursive, delete_nullable)
        self._remove_file()
        return result

    def get_file_path(self) -> Path:
        # noinspection PyTypeChecker
        return Path(self._get_attachments_directory_path(), self.file_name)

    def get_file_content(self) -> bytes:
        path = self.get_file_path()
        return path.read_bytes()
