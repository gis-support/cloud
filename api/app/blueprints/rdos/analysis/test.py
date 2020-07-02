#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask.testing import FlaskClient

from app.tests.utils import BaseTest, TEST_DATA_DIR
from io import BytesIO
import pytest
import json
import os


@pytest.mark.analysis
class TestSettings(BaseTest):

    def test_settings_get(self, client):
        token = self.get_token(client)
        r = client.get(f'/api/analysis/settings?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['pn'] == None
        assert r.json['settings']['pk'] == None

    def test_settings_put(self, client):
        token = self.get_token(client, admin=True)
        settings = {
            "pk": "test",
            "pn": "test"
        }
        r = client.put(
            f'/api/analysis/settings?token={token}', data=json.dumps(settings))
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['pn'] == settings['pn']
        assert r.json['settings']['pk'] == settings['pk']

    def test_distance_without_settings(self, client):
        token = self.get_token(client, admin=True)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        fid = 2
        data = {
            "buffer": 100*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'empty analysis settings settings'

    def test_incorrect_settings_pn(self, client):
        token = self.get_token(client, admin=True)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        fid = 2
        data = {
            "buffer": 100*1000,
            "name": "testowy punkt"
        }
        settings = {
            "pn": "test"
        }
        client.put(
            f'/api/analysis/settings?token={token}', data=json.dumps(settings))
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'invalid pn layer in settings'

    def test_incorrect_settings_pk(self, client):
        token = self.get_token(client, admin=True)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        fid = 2
        data = {
            "buffer": 100*1000,
            "name": "testowy punkt"
        }
        settings = {
            "pk": "test"
        }
        client.put(
            f'/api/analysis/settings?token={token}', data=json.dumps(settings))
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'invalid pn layer in settings'

    def test_distance_get(self, client):
        token = self.get_token(client, admin=True)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        # Parki narodowe
        pn_file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'pn.dbf'), 'rb').read())), 'pn.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'pn.prj'), 'rb').read())), 'pn.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'pn.shx'), 'rb').read())), 'pn.shx'),
            'file[3]': (BytesIO((open(os.path.join(path, 'pn.shp'), 'rb').read())), 'pn.shp'),
            'name': 'pn',
            'epsg': '2180',
            'encoding': 'cp1250'
        }
        r = client.post('/api/layers?token={}'.format(token), data=pn_file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid_pn = r.json['layers']['id']
        # Parki krajobrazowe
        pk_file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'pk.dbf'), 'rb').read())), 'pk.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'pk.prj'), 'rb').read())), 'pk.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'pk.shx'), 'rb').read())), 'pk.shx'),
            'file[3]': (BytesIO((open(os.path.join(path, 'pk.shp'), 'rb').read())), 'pk.shp'),
            'name': 'pk',
            'epsg': '2180',
            'encoding': 'cp1250'
        }
        r = client.post('/api/layers?token={}'.format(token), data=pk_file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid_pk = r.json['layers']['id']
        # Warstwa do testów
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        fid = 2
        # Zapisanie ustawień
        settings = {
            "pn": lid_pn,
            "pk": lid_pk
        }
        client.put(
            f'/api/analysis/settings?token={token}', data=json.dumps(settings))
        # Analiza 100km od punktów z Dolnego Śląska
        data = {
            "buffer": 100*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 200
        assert r.json
        assert len(r.json['distance']['pk']) == 0
        assert len(r.json['distance']['pn']) == 0
        # Analiza 300km
        data = {
            "buffer": 300*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 200
        assert r.json
        assert len(r.json['distance']['pk']) == 2
        assert len(r.json['distance']['pn']) == 0
        # Analiza 400km
        data = {
            "buffer": 400*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 200
        assert r.json
        assert len(r.json['distance']['pk']) == 15
        assert len(r.json['distance']['pn']) == 2
        # Analiza 500km
        data = {
            "buffer": 500*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 200
        assert r.json
        assert len(r.json['distance']['pk']) == 17
        assert len(r.json['distance']['pn']) == 2

    def test_distance_xlsx_get(self, client: FlaskClient):
        token = self.get_token(client, admin=True)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        # Parki narodowe
        pn_file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'pn.dbf'), 'rb').read())), 'pn.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'pn.prj'), 'rb').read())), 'pn.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'pn.shx'), 'rb').read())), 'pn.shx'),
            'file[3]': (BytesIO((open(os.path.join(path, 'pn.shp'), 'rb').read())), 'pn.shp'),
            'name': 'pn',
            'epsg': '2180',
            'encoding': 'cp1250'
        }
        r = client.post('/api/layers?token={}'.format(token), data=pn_file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid_pn = r.json['layers']['id']
        # Parki krajobrazowe
        pk_file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'pk.dbf'), 'rb').read())), 'pk.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'pk.prj'), 'rb').read())), 'pk.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'pk.shx'), 'rb').read())), 'pk.shx'),
            'file[3]': (BytesIO((open(os.path.join(path, 'pk.shp'), 'rb').read())), 'pk.shp'),
            'name': 'pk',
            'epsg': '2180',
            'encoding': 'cp1250'
        }
        r = client.post('/api/layers?token={}'.format(token), data=pk_file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid_pk = r.json['layers']['id']
        # Warstwa do testów
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        fid = 2
        # Zapisanie ustawień
        settings = {
            "pn": lid_pn,
            "pk": lid_pk
        }
        client.put(
            f'/api/analysis/settings?token={token}', data=json.dumps(settings))
        # Analiza 100km od punktów z Dolnego Śląska
        data = {
            "buffer": 100*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}/xlsx?token={token}', data=json.dumps(data))

        assert r.status_code == 200

    def test_intersection_json(self, client: FlaskClient):
        token = self.get_token(client, admin=True)

        # Warstwa do testów
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_3857.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_3857.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']

        data = {  # bbox Polski
          "geometry": {
            "coordinates": [
              [
                [
                  14.1228848600001,
                  49.002046518
                ],
                [
                  14.1228848600001,
                  54.836416667
                ],
                [
                  24.1457830750001,
                  54.836416667
                ],
                [
                  24.1457830750001,
                  49.002046518
                ],
                [
                  14.1228848600001,
                  49.002046518
                ]
              ]
            ],
            "type": "Polygon"
          }
        }
        r = client.post(
            f'/api/analysis/intersection/{lid}?token={token}&response_type=json', data=json.dumps(data)
        )

        assert r.status_code == 200
        assert r.json == {
          "data": [
            {
              "ID_BUFORA1": 0,
              "ID_BUFORA_": 21408,
              "ID_BUFOR_1": 0,
              "ID_TECHNIC": 829372,
              "IIP_IDENTY": "c606b01a-76c8-480d-9470-f24ca0d7a613",
              "IIP_PRZEST": "PL.PZGIK.200",
              "IIP_WERSJA": "Thu, 05 May 2016 18:20:48 GMT",
              "JPT_ID": 1311516,
              "JPT_JOR_ID": 0,
              "JPT_KJ_IIP": "EGIB",
              "JPT_KJ_I_1": "30",
              "JPT_KJ_I_2": None,
              "JPT_KJ_I_3": None,
              "JPT_KOD_JE": "30",
              "JPT_KOD__1": None,
              "JPT_NAZWA1": None,
              "JPT_NAZWA_": "wielkopolskie",
              "JPT_OPIS": None,
              "JPT_ORGAN1": "NZN",
              "JPT_ORGAN_": None,
              "JPT_SJR_KO": "WOJ",
              "JPT_SPS_KO": "UZG",
              "JPT_WAZNA_": "NZN",
              "Shape_Area": 3.9321954,
              "Shape_Leng": 18.408173,
              "WAZNY_DO": None,
              "WAZNY_OD": "Wed, 26 Sep 2012 00:00:00 GMT",
              "WERSJA_DO": None,
              "WERSJA_OD": "Thu, 05 May 2016 00:00:00 GMT",
              "id": 1
            }
          ]
        }

    def test_intersection_json_no_match(self, client: FlaskClient):
        token = self.get_token(client, admin=True)

        # Warstwa do testów
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_3857.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_3857.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']

        data = { "geometry": { # bbox lubelskiego
            "type": "Polygon",
            "coordinates": [
              [
                [
                  20.994873046875,
                  52.42252295423907
                ],
                [
                  21.258544921875,
                  50.240178884797025
                ],
                [
                  24.32373046875,
                  50.240178884797025
                ],
                [
                  24.01611328125,
                  52.30176096373671
                ],
                [
                  20.994873046875,
                  52.42252295423907
                ]
              ]
            ]
          }
        }

        r = client.post(
            f'/api/analysis/intersection/{lid}?token={token}&response_type=json', data=json.dumps(data)
        )

        assert r.status_code == 200
        assert r.json == {"data": []}

    def test_intersection_xlsx(self, client: FlaskClient):
        token = self.get_token(client, admin=True)

        # Warstwa do testów
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_3857.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_3857.geojson'),
            'name': 'test_points'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']

        data = {  # bbox Polski
          "geometry": {
            "coordinates": [
              [
                [
                  14.1228848600001,
                  49.002046518
                ],
                [
                  14.1228848600001,
                  54.836416667
                ],
                [
                  24.1457830750001,
                  54.836416667
                ],
                [
                  24.1457830750001,
                  49.002046518
                ],
                [
                  14.1228848600001,
                  49.002046518
                ]
              ]
            ],
            "type": "Polygon"
          }
        }

        r = client.post(
            f'/api/analysis/intersection/{lid}?token={token}&response_type=xlsx', data=json.dumps(data)
        )

        assert r.status_code == 200
