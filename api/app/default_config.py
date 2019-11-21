# !usr/bin/python
# -*- coding: utf-8 -*-


# Sklonuj ten plik z nazwą local_config.py żeby wprowadzić zmiany do konfiguracji aplikacji


class Config(object):
    DBNAME = 'cloud'
    DBUSER = 'docker'
    DBPASS = 'docker'
    DBPORT = 5432
    DBHOST = 'cloud-db'
    HOST = 'http://localhost'
    REDIS_URL = "redis://:password@cloud-redis:6379/0"
    SECRET_KEY = 'test'
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DBNAME = 'cloud-testing'
