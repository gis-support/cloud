from playhouse.postgres_ext import PostgresqlExtDatabase

from app.blueprints.attachments.models import Attachment
from app.blueprints.layers.dicts.dict import Dict
from app.blueprints.layers.tags.models import Tag, LayerTag
from app.blueprints.projects.models import Project
from app.blueprints.settings.models import Setting
from app.db.migrations.migration import Migration


def create_tables(database: PostgresqlExtDatabase):
    models = [
        Tag,
        LayerTag,
        Dict,
        Attachment,
        Project,
        Setting,
    ]

    for model in models:
        try:
            model.create_table(True)
        except Exception as e:
            print(f"ERROR CREATING TABLE {model._meta.table_name}")
            print(str(e))
