# !usr/bin/python
# -*- coding: utf-8 -*-


# Sklonuj ten plik z nazwą local_config.py żeby wprowadzić zmiany do konfiguracji aplikacji

from os import environ, path as op


class Config(object):
    DBNAME = 'cloud'
    DBUSER = 'docker'
    DBPASS = 'nielogowacsienategousera'
    DBPORT = 5432
    APP_NAME = environ.get('CONTAINER_BASENAME', 'cloud')
    DBHOST = f'{APP_NAME}-db-prod'
    APP_HOST = environ.get('APP_PROD_HOST_URL', 'cloud.gis.support')
    APP_PORT = environ.get('APP_PROD_API_PORT', 4999)
    REDIS_URL = f"redis://@{APP_NAME}-redis-prod:6379/0"
    SECRET_KEY = 'test'
    DEBUG = False
    TESTING = False

    ROOT_DIRECTORY = op.abspath(op.dirname(op.dirname(__file__)))

    STATIC = op.join(ROOT_DIRECTORY, 'static')
    UPLOADS = op.join(ROOT_DIRECTORY, "uploads")


class DevelopmentConfig(Config):
    DEBUG = True
    APP_PORT = environ.get('APP_DEV_API_PORT', 5001)
    APP_HOST = environ.get('APP_DEV_HOST_URL', 'localhost')
    APP_NAME = environ.get('CONTAINER_BASENAME', 'cloud')
    REDIS_URL = f"redis://@{APP_NAME}-redis:6379/0"
    DBHOST = f'{APP_NAME}-db'


class TestingConfig(Config):
    TESTING = True
    APP_NAME = environ.get('CONTAINER_BASENAME', 'cloud')
    DBNAME = 'cloud-testing'
    DBHOST = f'{APP_NAME}-db'
    REDIS_URL = f"redis://@{APP_NAME}-redis:6379/1"
