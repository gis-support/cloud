from app.db.base_model import BaseModel
from peewee import TextField, BooleanField
from playhouse.shortcuts import model_to_dict
import os


class Service(BaseModel):
    name = TextField(null=False)
    url = TextField(null=False)
    layers = TextField(null=False)
    group = TextField(null=True, default=os.environ['DEFAULT_GROUP'])

    @staticmethod
    def get_services(group):
        groups = set([group, os.environ['DEFAULT_GROUP']])
        return [row for row in Service.select().where(Service.group << groups).dicts()]

    @staticmethod
    def add_service(data):
        model = {
            'name': data['name'],
            'url': data['url'],
            'layers': data['layers'],
            'group': data['group']
        }
        service = Service.create(**model)
        return model_to_dict(service)

    @staticmethod
    def delete_service(sid):
        service = Service.delete().where(Service.id == sid).execute()
        return service

    @staticmethod
    def validate(data):
        counter = 0
        for key in ['name', 'url', 'layers', 'group']:
            if not data.get(key):
                return f'{key} is invalid', 409
        return None, None

    @staticmethod
    def check_permission(sid, group):
        groups = set([group, os.environ['DEFAULT_GROUP']])
        query = Service.select().where(
            Service.group << groups,
            Service.id == sid).dicts()
        return (None, None) if bool([row for row in query]) else ('permission denied', 403)
