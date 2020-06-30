from peewee import Model

from app.db.database import database


class BaseModel(Model):
    class Meta:
        database = database
        schema = "public"

    @classmethod
    def ensure_schema_exists(cls):
        sql = f"""CREATE SCHEMA IF NOT EXISTS {cls._meta.schema};"""
        cls._meta.database.execute_sql(sql)

    @classmethod
    def create_table(cls, safe=True, **options):
        with cls._meta.database.atomic():
            cls.ensure_schema_exists()
            super().create_table(safe, **options)
