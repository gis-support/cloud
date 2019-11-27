#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest, TEST_DATA_DIR
import json
import pytest
import os
from io import BytesIO


@pytest.mark.layers
class TestLayers(BaseTest):

    def test_layers_get_correct(self, client):
        token = self.get_token(client)
        r = client.get('/api/layers?token={}'.format(token))
        assert r.status_code == 200
        assert r.json
        assert r.json['layers'] == []

    def test_layers_post_geojson_prg(self, client):
        token = self.get_token(client)
        self.add_geojson_prg(client, token)
        r = client.get('/api/layers?token={}'.format(token))
        assert r.status_code == 200
        assert r.json
        assert r.json['layers']
        assert len(r.json['layers']) == 1
        assert r.json['layers'][0]['name'] == 'wojewodztwa'

    def test_layers_post_geojson_prg_transform(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_3857.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_3857.geojson'),
            'name': 'wojewodztwa'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'wojewodztwa'
        return r.json['layers']['id']
        r = client.get('/api/layers?token={}'.format(token))

    def test_layers_post_shapefile(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'correct.dbf'), 'rb').read())), 'correct.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'correct.prj'), 'rb').read())), 'correct.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'correct.shx'), 'rb').read())), 'correct.shx'),
            'file[3]': (BytesIO((open(os.path.join(path, 'correct.shp'), 'rb').read())), 'correct.shp'),
            'name': 'wojewodztwa'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'wojewodztwa'
        return r.json['layers']['id']

    def test_layers_post_shapefile_no_attrs(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'correct.prj'), 'rb').read())), 'correct.prj'),
            'file[1]': (BytesIO((open(os.path.join(path, 'correct.shp'), 'rb').read())), 'correct.shp'),
            'file[2]': (BytesIO((open(os.path.join(path, 'correct.shx'), 'rb').read())), 'correct.shx'),
            'name': 'wojewodztwa'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'wojewodztwa'
        return r.json['layers']['id']

    def test_layers_post_shapefile_invalid_file(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'correct.dbf'), 'rb').read())), 'correct.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'correct.prj'), 'rb').read())), 'correct.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'correct.shp'), 'rb').read())), 'correct.shp'),
            'name': 'wojewodztwa'
        }
        from osgeo import gdal
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        gdal.UseExceptions()
        assert r.status_code == 401
        assert r.json
        assert r.json['error'] == 'file is invalid'

    def test_layers_post_shapefile_without_prj(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'correct.dbf'), 'rb').read())), 'correct.dbf'),
            'file[2]': (BytesIO((open(os.path.join(path, 'correct.shp'), 'rb').read())), 'correct.shp'),
            'file[3]': (BytesIO((open(os.path.join(path, 'correct.shx'), 'rb').read())), 'correct.shx'),
            'name': 'wojewodztwa'
        }
        from osgeo import gdal
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        gdal.UseExceptions()
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'wojewodztwa'
        return r.json['layers']['id']

    def test_layers_delete_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 200
        assert r.json
        assert r.json['layers'] == 'wojewodztwa deleted'

    def test_layers_delete_invalid_id(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete('/api/layers/1?token={}'.format(token))
        assert r.status_code == 401
        assert r.json
        assert r.json['error'] == 'invalid layer id'

    def test_layers_delete_layer_not_exists(self, client):
        token = self.get_token(client)
        r = client.delete(
            '/api/layers/vJoqBpbA8go4nogNZ?token={}'.format(token))
        assert r.status_code == 401
        assert r.json
        assert r.json['error'] == 'layer not exists'

    def test_layers_delete_layer_access_denied(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        token = self.get_token(client)
        r = client.delete('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'


@pytest.mark.layerssettings
class TestLayersSettings(BaseTest):

    def test_settings_get_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.get(f'/api/layers/{lid}/settings?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['id'] == lid
        assert len(r.json['settings']['columns'].keys()) == 30

    def test_settings_delete_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        client.delete(f'/api/layers/{lid}/settings?token={token}', data=json.dumps({"column_name": "JPT_NAZWA_"}))
        r = client.get(f'/api/layers/{lid}/settings?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['id'] == lid
        assert len(r.json['settings']['columns'].keys()) == 29

    def test_settings_delete_not_exists_column(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete(f'/api/layers/{lid}/settings?token={token}', data=json.dumps({"column_name": "test"}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column not exists'

    def test_settings_delete_restricted_column(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete(f'/api/layers/{lid}/settings?token={token}', data=json.dumps({"column_name": "geometry"}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column restricted'
        r = client.delete(f'/api/layers/{lid}/settings?token={token}', data=json.dumps({"column_name": "id"}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column restricted'

    def test_settings_delete_empty_column(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete(f'/api/layers/{lid}/settings?token={token}', data=json.dumps({}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column_name required'
