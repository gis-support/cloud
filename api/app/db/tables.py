from playhouse.postgres_ext import PostgresqlExtDatabase
from app.blueprints.layers.tags.models import Tag, LayerTag

def create_tables(database: PostgresqlExtDatabase):
    models = [
        Tag,
        LayerTag
    ]

    database.create_tables(models)