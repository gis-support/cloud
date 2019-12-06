from app.db.general import BaseModel
from peewee import TextField


class Attachment(BaseModel):
    link = TextField(null=True)
    group = TextField(null=True, default="default")
