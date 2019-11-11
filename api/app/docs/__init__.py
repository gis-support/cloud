#!/usr/bin/python
# -*- coding: utf-8 -*-

from flasgger import Swagger, swag_from
import os

def create_swagger(app):
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Cloud",
            "description": "",
            "contact": {
                "responsibleOrganization": "",
                "responsibleDeveloper": "",
                "email": "",
                "url": "",
            },
            "termsOfService": "",
            "version": "0.1"
        },
        "host": app.config['HOST'],
        "basePath": "/api/",
        "schemes": [
            "http",
            "https"
        ],
        "operationId": "getmyData"
    }
    config = {
            "headers": [
        ],
        "specs": [
            {
                "endpoint": 'api',
                "route": '/api/docs/api.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    return Swagger(app, template=template, config=config)

def swagger(path, filename):
    def wrapper(func):
        @swag_from(os.path.abspath(os.path.join(os.path.dirname(path), filename)))
        def func2(*args, **kwargs):
            return func(*args, **kwargs)
        func2.__name__ = func.__name__
        return func2
    return wrapper