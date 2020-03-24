#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        # Analiza 500km
        data = {
            "buffer": 500*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 200
        assert r.json
        assert len(r.json['distance']['pk']) == 2
        assert len(r.json['distance']['pn']) == 0
        # Analiza 700km
        data = {
            "buffer": 700*1000,
            "name": "testowy punkt"
        }
        r = client.post(
            f'/api/analysis/distance/{lid}/{fid}?token={token}', data=json.dumps(data))
        assert r.status_code == 200
        assert r.json
        assert len(r.json['distance']['pk']) == 17
        assert len(r.json['distance']['pn']) == 2
