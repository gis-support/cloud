#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest
import json
import pytest


@pytest.mark.settings
class TestSettings(BaseTest):

    # APP NAME

    def test_get_app_name(self, client):
        result = client.get('/api/app_name')
        assert result.status_code == 200
        assert result.json

    def test_put_app_name_correct(self, client):
        token = self.get_token(client, admin=True)
        result = client.put(f'/api/app_name?token={token}', data=json.dumps({'app_name': "GIS Support Cloud"}))
        assert result.status_code == 200
        assert result.json
        assert result.json["settings"] == "app name changed"

    def test_put_app_name_empty_json(self, client):
        token = self.get_token(client, admin=True)
        result = client.put(f'/api/app_name?token={token}', data=json.dumps({}))
        assert result.status_code == 400
        assert result.json
        assert result.json["error"] == "app name is required"
    
    def test_put_app_name_empty_name(self, client):
        token = self.get_token(client, admin=True)
        result = client.put(f'/api/app_name?token={token}', data=json.dumps({"app_name": ""}))
        assert result.status_code == 400
        assert result.json
        assert result.json["error"] == "app name is required"
        