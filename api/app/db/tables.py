from playhouse.postgres_ext import PostgresqlExtDatabase

from app.blueprints.attachments.models import Attachment
from app.blueprints.layers.dicts.dict import Dict
from app.blueprints.layers.tags.models import Tag, LayerTag
from app.db.migrations.migration import Migration


def create_tables(database: PostgresqlExtDatabase):
    models = [
        Tag,
        LayerTag,
        Dict,
        Attachment,
    ]

    database.create_tables(models)