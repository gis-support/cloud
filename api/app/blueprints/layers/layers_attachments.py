from typing import List, Iterable

from app.blueprints.attachments.models import Attachment
from app.blueprints.layers.utils import ATTACHMENTS_COLUMN_NAME
from app.helpers.layer import Layer
from app.db.database import database

from psycopg2 import sql as psysql


class LayerNotSupportedError(Exception):
    pass

class LayerAlreadySupportedError(Exception):
    pass


class LayerAttachmentsManager:

    serializer_separator = ";"

    def __init__(self, layer: Layer):
        self.layer = layer

    @classmethod
    def create_attachments_column(cls, layer: Layer):
        if cls.does_layer_have_attachments_column(layer):
            raise LayerAlreadySupportedError(f"column {ATTACHMENTS_COLUMN_NAME} already exists")

        sql = psysql.SQL("ALTER TABLE {} ADD COLUMN {} TEXT;").format(
            psysql.Identifier(layer.name),
            psysql.Identifier(ATTACHMENTS_COLUMN_NAME)
        )

        database.execute_sql(sql)

    @classmethod
    def does_layer_have_attachments_column(cls, layer: Layer) -> bool:
        columns = layer.columns()
        return ATTACHMENTS_COLUMN_NAME in columns

    @classmethod
    def from_layer(cls, layer: Layer) -> "LayerAttachmentsManager":
        if not cls.does_layer_have_attachments_column(layer):
            raise LayerNotSupportedError(f"layer does not contain column {ATTACHMENTS_COLUMN_NAME}")

        return cls(layer)

    def _serialize_attachments_column_value(self, attachments_ids: List[int]) -> str:
        ids_str = map(str, attachments_ids)
        serialized = self.serializer_separator.join(ids_str)
        return serialized

    def _deserialize_attachments_column_value(self, column_value: str) -> List[int]:
        split = column_value.split(self.serializer_separator)
        ids = map(int, split)
        return list(ids)

    def get_attachments_ids_of_object(self, object_id: int) -> List[int]:
        sql = psysql.SQL("SELECT {} FROM {} WHERE id = {};").format(
            psysql.Identifier(ATTACHMENTS_COLUMN_NAME),
            psysql.Identifier(self.layer.name),
            psysql.Literal(object_id)
        )
        cursor = database.execute_sql(sql)

        row = cursor.fetchone()
        if row is None:
            raise IndexError(f"object of ID '{object_id}' does not exists")

        value = row[0]
        if value is None:
            return []

        ids = self._deserialize_attachments_column_value(value)
        return ids

    def set_attachments_ids_of_object(self, object_id: int, attachments_ids: List[int]):
        value = self._serialize_attachments_column_value(attachments_ids)

        sql = psysql.SQL("UPDATE {} SET {} = {} WHERE id = {};").format(
            psysql.Identifier(self.layer.name),
            psysql.Identifier(ATTACHMENTS_COLUMN_NAME),
            psysql.Literal(value),
            psysql.Literal(object_id)
        )

        database.execute_sql(sql)

    def add_attachment_to_object(self, object_id: int, attachment_id: int):
        ids = self.get_attachments_ids_of_object(object_id)

        if attachment_id not in ids:
            ids.append(attachment_id)

        self.set_attachments_ids_of_object(object_id, ids)

    def get_attachments_of_object(self, object_id: int) -> Iterable[Attachment]:
        ids = self.get_attachments_ids_of_object(object_id)
        attachments = Attachment.select().where(Attachment.id.in_(ids))
        for attachment in attachments:
            yield attachment

    def remove_attachment_from_object(self, object_id: int, attachment_id: int):
        ids = self.get_attachments_ids_of_object(object_id)
        ids = [id_ for id_ in ids if id_ != attachment_id]
        self.set_attachments_ids_of_object(object_id, ids)
