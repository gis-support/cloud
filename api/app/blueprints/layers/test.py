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
        column_to_delete = "JPT_NAZWA_"
        r = client.delete(f'/api/layers/{lid}/settings?token={token}',
                          data=json.dumps({"column_name": column_to_delete}))
        assert r.status_code == 200
        assert r.json
        assert r.json['settings'] == f'{column_to_delete} deleted'
        r = client.get(f'/api/layers/{lid}/settings?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['id'] == lid
        assert len(r.json['settings']['columns'].keys()) == 29

    def test_settings_delete_not_exists_column(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps({"column_name": "test"}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column not exists'

    def test_settings_delete_restricted_column(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete(f'/api/layers/{lid}/settings?token={token}',
                          data=json.dumps({"column_name": "geometry"}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column restricted'
        r = client.delete(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps({"column_name": "id"}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column restricted'

    def test_settings_delete_empty_column(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.delete(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps({}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'column_name required'

    def test_settings_add_column_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        new_column = {
            "column_name": "test",
            "column_type": "character varying"
        }
        r = client.post(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps(new_column))
        assert r.status_code == 200
        assert r.json
        assert r.json['settings'] == f"{new_column['column_name']} added"
        r = client.get(f'/api/layers/{lid}/settings?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['id'] == lid
        assert len(r.json['settings']['columns'].keys()) == 31
        assert r.json['settings']['columns'][new_column['column_name']
                                             ] == new_column['column_type']

    def test_settings_add_column_exists(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        new_column = {
            "column_name": "JPT_NAZWA_",
            "column_type": "character varying"
        }
        r = client.post(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps(new_column))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == "column exists"

    def test_settings_add_column_ivalid_type(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        new_column = {
            "column_name": "test",
            "column_type": "serial"
        }
        r = client.post(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps(new_column))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == "invalid column type"

    def test_settings_change_name(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        new_column = {
            "layer_name": "test"
        }
        r = client.post(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps(new_column))
        assert r.status_code == 200
        assert r.json
        assert r.json['settings'] != lid
        new_lid = r.json['settings']
        r = client.get(f'/api/layers/{lid}/settings?token={token}')
        assert r.status_code == 401
        assert r.json
        assert r.json['error'] == 'layer not exists'
        r = client.get(f'/api/layers/{new_lid}/settings?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['name'] == new_column['layer_name']


@pytest.mark.styles
class TestLayersStyles(BaseTest):

    def test_styles_get_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['fill-color'] == '255,255,255,0.4'
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '2'

    def test_styles_set_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        new_fill_color = '0,0,0,0.4'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps({'fill-color': new_fill_color}))
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['fill-color'] == new_fill_color
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['fill-color'] == new_fill_color
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '2'
        new_stroke_color = '255,255,255,255'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps({'stroke-color': new_stroke_color}))
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['stroke-color'] == new_stroke_color
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['fill-color'] == new_fill_color
        assert r.json['style']['stroke-color'] == new_stroke_color
        assert r.json['style']['stroke-width'] == '2'

    def test_styles_invalid_property(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        new_fill_color = '0,0,0,0.4'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps({'test-color': new_fill_color}))
        # nothing change
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['fill-color'] == '255,255,255,0.4'
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '2'
        # TODO validate color values + width
