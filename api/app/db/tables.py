from playhouse.postgres_ext import PostgresqlExtDatabase

from app.blueprints.layers.dicts.dict import Dict
from app.blueprints.layers.tags.models import Tag, LayerTag

def create_tables(database: PostgresqlExtDatabase):
    models = [
        Tag,
        LayerTag,
        Dict,
    ]

    database.create_tables(models)