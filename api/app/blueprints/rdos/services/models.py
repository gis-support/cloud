from app.blueprints.projects.models import Project
from app.db.base_model import BaseModel
from peewee import TextField, BooleanField, AutoField
from playhouse.shortcuts import model_to_dict
import os


class Service(BaseModel):
    id = AutoField(primary_key=True)
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

    @classmethod
    def delete_service(cls, sid):
        with cls._meta.database.atomic():
            service = Service.get(Service.id == sid)
            service._remove_self_from_projects()
            service.delete_instance()

        return service.id

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

    def _remove_self_from_projects(self):
        query = Project.select()
        row: Project
        for row in query:
            services_ids = row.service_layers_ids
            services_ids = [id_ for id_ in services_ids if id_ != self.id]
            row.service_layers_ids = services_ids
            row.save()
