from peewee import AutoField, TextField, IntegerField, fn, Cast
from playhouse.postgres_ext import BinaryJSONField

from app.db.base_model import BaseModel
from app.db.database import database
from app.db.fields import GeometryField


class Project(BaseModel):
    class Meta:
        schema = "system"

    id = AutoField(primary_key=True)
    name = TextField()
    owner_name = TextField()
    active_layer_id = TextField()
    additional_layers_ids = BinaryJSONField(default=[])
    service_layers_ids = BinaryJSONField(default=[])
    map_center = GeometryField("point", 4326)
    map_zoom = IntegerField()

    @classmethod
    def update_active_layer_id(cls, old_layer_id: str, new_layer_id: str):
        cls.update(active_layer_id=new_layer_id).where(cls.active_layer_id == old_layer_id).execute()

    @classmethod
    def update_additional_layers_ids(cls, old_layer_id: str, new_layer_id: str):
        cls.update(additional_layers_ids=Cast(
            fn.REPLACE(
                Cast(cls.additional_layers_ids, "text"),
                old_layer_id,
                new_layer_id
            ),
            "jsonb")
        ).execute()

    @classmethod
    def delete_additional_layer_id(cls, layer_id: str):
        database.execute_sql("""
        UPDATE system.project SET additional_layers_ids = additional_layers_ids-%s;
        """, (layer_id, ))