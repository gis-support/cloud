#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.db.base_model import BaseModel
from peewee import TextField, DoesNotExist
from playhouse.shortcuts import model_to_dict
import os


class Settings(BaseModel):
    pn = TextField(null=True)
    pk = TextField(null=True)

    @staticmethod
    def get_settings():
        try:
            settings = Settings.get()
        except DoesNotExist:
            settings = Settings.create()
        setting_dict = model_to_dict(settings)
        del setting_dict['id']
        return setting_dict

    @staticmethod
    def update_settings(data):
        try:
            settings = Settings.get()
        except DoesNotExist:
            settings = Settings.create()
        for key in [i for i in Settings._meta.fields.keys() if i != 'id']:
            if data.get(key):
                setattr(settings, key, data[key])
        return settings.save()
