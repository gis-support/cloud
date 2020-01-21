#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest
import pytest
import json
import os


@pytest.mark.services
class TestServices(BaseTest):

    def test_services_public(self, client):
        token = self.get_token(client)
        sid = self.add_service(client, token)
        r = client.get(
            f'/api/services?token={token}')
        assert r.status_code == 200
        assert r.json
        assert len(r.json['services']) == 1

    def test_services_private(self, client):
        token = self.get_token(client, default_group=False)
        sid = self.add_service(client, token, public=False)
        r = client.get(
            f'/api/services?token={token}')
        assert r.status_code == 200
        assert r.json
        assert len(r.json['services']) == 1
        token = self.get_token(client)
        r = client.get(
            f'/api/services?token={token}')
        assert r.status_code == 200
        assert r.json
        assert len(r.json['services']) == 0

    def test_services_delete(self, client):
        token = self.get_token(client)
        sid = self.add_service(client, token)
        r = client.delete(
            f'/api/services/{sid}?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['sid'] == 1
        r = client.get(
            f'/api/services?token={token}')
        assert r.status_code == 200
        assert r.json
        assert len(r.json['services']) == 0

    def test_services_empty_keys(self, client):
        token = self.get_token(client)
        request = {
            'name': 'geoportal prg',
            'url': 'https://integracja.gugik.gov.pl/cgi-bin/KrajowaIntegracjaNumeracjiAdresowej',
            'layers': 'prg-adresy,prg-ulice,prg-place'
        }
        for key in request:
            request_invalid = request.copy()
            del request_invalid[key]
            r = client.post(
                f'/api/services?token={token}', data=json.dumps(request_invalid))
            assert r.status_code == 409
            assert r.json
            assert r.json['error'] == f'{key} is invalid'

    def test_services_private_delete(self, client):
        token = self.get_token(client, default_group=False)
        sid = self.add_service(client, token, public=False)
        token = self.get_token(client)
        r = client.delete(
            f'/api/services/{sid}?token={token}')
        assert r.status_code == 403
        assert r.json['error'] == 'permission denied'
