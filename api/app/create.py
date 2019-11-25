#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_cors import CORS
from flask_redis import FlaskRedis
from app.docs import create_swagger
from app.db import create_db
from app.blueprints.auth.routings import mod_auth
from app.blueprints.layers.routings import mod_layers
from app.blueprints.permissions.routings import mod_permissions
from hashids import Hashids
try:
    from app.local_config import *
except:
    from app.default_config import *


def create_app(config='development'):
    app = Flask(__name__.split('.')[0])
    app._cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(load_config(config))
    app._swagger = create_swagger(app)
    app._db = create_db(app.config)
    app._redis = FlaskRedis(app)
    app._hashids = Hashids(salt=app.config['SECRET_KEY'])
    app.register_blueprint(mod_auth, url_prefix='/api')
    app.register_blueprint(mod_layers, url_prefix='/api')
    app.register_blueprint(mod_permissions, url_prefix='/api')
    return app


def load_config(config):
    if config == 'production':
        return Config
    elif config == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
