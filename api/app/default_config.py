# !usr/bin/python
# -*- coding: utf-8 -*-


# Sklonuj ten plik z nazwą local_config.py żeby wprowadzić zmiany do konfiguracji aplikacji


class Config(object):
    DBNAME = 'cloud'
    DBUSER = 'docker'
    DBPASS = 'nielogowacsienategousera'
    DBPORT = 5432
    DBHOST = 'cloud-db'
    APP_HOST = 'cloud.gis.support'
    APP_PORT = 4999
    REDIS_URL = "redis://@cloud-redis:6379/0"
    SECRET_KEY = 'test'
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    APP_PORT = 5001
    APP_HOST = 'localhost'


class TestingConfig(Config):
    TESTING = True
    DBNAME = 'cloud-testing'
