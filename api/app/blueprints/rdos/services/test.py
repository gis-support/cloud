#!/usr/bin/python
# -*- coding: utf-8 -*-
from copy import deepcopy

from flask.testing import FlaskClient
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

    def test_delete_service_get_project(self, client: FlaskClient):
        token = self.get_token(client)
        service_1_id = self.add_service(client, token)
        service_2_id = self.add_service(client, token)

        layer_id = self.add_geojson_prg(client, token)

        project_data = {
            "name": "name",
            "active_layer_id": layer_id,
            "map_center": {
                "coordinates": [
                  21,
                  52
                ],
                "type": "Point"
            },
            "map_zoom": 11,
            "service_layers_ids": [service_1_id, service_2_id],
            "additional_layers_ids": []
        }

        project_id = client.post("/api/projects",
                                 data=json.dumps(project_data),
                                 query_string={"token": token}
                                 ).json["data"]
        expected_data = deepcopy(project_data)
        expected_data["id"] = project_id
        expected_data["permission_to_each_additional_layer"] = True

        actual_data_before_delete_service = client.get(f"/api/projects/{project_id}", query_string={"token": token}).json["data"]
        assert actual_data_before_delete_service == expected_data

        client.delete(f'/api/services/{service_1_id}?token={token}')
        expected_data["service_layers_ids"] = [service_2_id]

        actual_data_after_delete_service = client.get(f"/api/projects/{project_id}", query_string={"token": token}).json["data"]
        assert expected_data == actual_data_after_delete_service
