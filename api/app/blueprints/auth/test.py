#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest
import json
import pytest


@pytest.mark.auth
class TestAuth(BaseTest):

    def test_register_correct(self, client):
        self.register(client)

    def test_register_duplicate(self, client):
        user, password = self.register(client)
        r = client.post('/api/register',
                        data=json.dumps({'user': user, 'password': password}))
        assert r.status_code == 409
        assert r.json
        assert r.json['error'] == 'user exists'

    def test_login_correct(self, client):
        token = self.get_token(client)
        assert len(token) > 0

    def test_login_invalid(self, client):
        self.register(client)
        r = client.post(
            '/api/login', data=json.dumps({'user': 'test', 'password': '?'}))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'invalid credentials'
