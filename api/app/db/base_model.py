from peewee import Model

from app.db.database import database

class BaseModel(Model):
    class Meta:
        database = database
