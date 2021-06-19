from app.db.base_model import BaseModel
from peewee import AutoField, TextField
from os import environ

class Setting(BaseModel):
    class Meta:
        schema = "system"

    id = AutoField()
    app_name = TextField(null=False, default=environ.get("CONTAINER_BASENAME"))
    # Additional space for other settings to add in future.

    @classmethod
    def get_app_name(cls) -> str:
        settings = cls.select().where(cls.id == 1)
        if settings.count() == 0:
            cls.create().save()
        return cls.select().where(cls.id == 1).dicts()[0]["app_name"]

    @classmethod
    def put_app_name(cls, payload: dict) -> (str, int):
        settings = cls.select().where(cls.id == 1)
        if settings.count() == 0:
            cls.create().save()
        cls.update({cls.app_name: payload["app_name"]}).where(cls.id == 1).execute()
        return "app name changed", 200