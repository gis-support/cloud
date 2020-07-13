#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Any, List

from flask import Response
from flask.testing import FlaskClient

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
        lid = self.add_geojson_prg(client, token)
        r = client.get('/api/layers?token={}'.format(token))
        assert r.status_code == 200
        assert r.json
        assert r.json['layers']
        assert len(r.json['layers']) == 1
        assert r.json['layers'][0]['name'] == 'wojewodztwa'
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0][0] == [
            16.714467009, 53.299132461]

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
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0][0] == [
            16.714467009, 53.299132461]

    def test_add_layer_with_features_with_empty_geometry(self, client):
        name = "test"
        file = "correct_with_empty_geom.geojson"

        token = self.get_token(client)

        path = os.path.join(TEST_DATA_DIR, 'layers', file)
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), file),
            'name': name
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 400
        assert r.json["error"] == "layer has at least one feature with empty geometry"

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
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0] == [
            16.714467009, 53.299132461]

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
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0] == [
            16.714467009, 53.299132461]

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
            'name': 'wojewodztwa',
            'epsg': '4326'
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
        self.add_geojson_prg(client, token)
        r = client.delete(f'/api/layers/test?token={token}')
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

    def test_layers_post_geojson_RL_38(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'RL-38.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'RL-38.geojson'),
            'name': 'RL-38'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['name'] == 'RL-38'
        assert r.json['layers']['features'] == 3
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0][0] == [
            18.878488648, 53.164468287]

    def test_layers_post_geojson_RL_37(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'RL-37.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'RL-37.geojson'),
            'name': 'RL-37'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['name'] == 'RL-37'
        assert r.json['layers']['features'] == 1
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0][0] == [
            17.028306997, 52.205571184]

    def test_layers_post_shp_correct_tranfsform(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'correct_3857.dbf'), 'rb').read())), 'correct_3857.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'correct_3857.prj'), 'rb').read())), 'correct_3857.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'correct_3857.shp'), 'rb').read())), 'correct_3857.shp'),
            'file[3]': (BytesIO((open(os.path.join(path, 'correct_3857.shx'), 'rb').read())), 'correct_3857.shx'),
            'file[4]': (BytesIO((open(os.path.join(path, 'correct_3857.cpg'), 'rb').read())), 'correct_3857.cpg'),
            'file[5]': (BytesIO((open(os.path.join(path, 'correct_3857.qpj'), 'rb').read())), 'correct_3857.qpj'),
            'name': 'wojewodztwa'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'wojewodztwa'
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0] == [
            16.714467009, 53.299132461]

    def test_layers_post_geojson_RL_48_error(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'RL-48-2.dbf'), 'rb').read())), 'RL-48-2.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'RL-48-2.shp'), 'rb').read())), 'RL-48-2.shp'),
            'file[2]': (BytesIO((open(os.path.join(path, 'RL-48-2.shx'), 'rb').read())), 'RL-48-2.shx'),
            'file[3]': (BytesIO((open(os.path.join(path, 'RL-48-2.cpg'), 'rb').read())), 'RL-48-2.cpg'),
            'name': 'RL-48'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'epsg not recognized'
        file_request_2 = {
            'file[0]': (BytesIO((open(os.path.join(path, 'RL-48.dbf'), 'rb').read())), 'RL-48.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'RL-48.prj'), 'rb').read())), 'RL-48.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'RL-48.shp'), 'rb').read())), 'RL-48.shp'),
            'file[3]': (BytesIO((open(os.path.join(path, 'RL-48.shx'), 'rb').read())), 'RL-48.shx'),
            'file[4]': (BytesIO((open(os.path.join(path, 'RL-48.cpg'), 'rb').read())), 'RL-48.cpg'),
            'file[5]': (BytesIO((open(os.path.join(path, 'RL-48.qpj'), 'rb').read())), 'RL-48.qpj'),
            'name': 'RL-48',
            'epsg': '2180'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request_2,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['name'] == 'RL-48'
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0] == [
            23.473214359, 52.080550359]

    def test_layers_post_invalid_encoding(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'invalid_encoding.dbf'), 'rb').read())), 'invalid_encoding.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'invalid_encoding.prj'), 'rb').read())), 'invalid_encoding.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'invalid_encoding.shp'), 'rb').read())), 'invalid_encoding.shp'),
            'file[3]': (BytesIO((open(os.path.join(path, 'invalid_encoding.shx'), 'rb').read())), 'invalid_encoding.shx'),
            'file[4]': (BytesIO((open(os.path.join(path, 'invalid_encoding.cpg'), 'rb').read())), 'invalid_encoding.cpg'),
            'file[5]': (BytesIO((open(os.path.join(path, 'invalid_encoding.qpj'), 'rb').read())), 'invalid_encoding.qpj'),
            'name': 'invalid_encoding'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 200
        assert r.json['features'][0]['geometry']['coordinates'][0][0] == [
            22.65563999, 51.718238491]


@pytest.mark.layerssettings
class TestLayersSettings(BaseTest):

    def post_create_column(self, client: FlaskClient, layer_id: str, data: dict, token) -> Response:
        query_string = {"token": token}

        result = client.post(f"/api/layers/{layer_id}/settings", data=json.dumps(data), query_string=query_string)
        return result

    def get_columns(self, client: FlaskClient, layer_id: str, token: str) -> Response:
        query_string = {"token": token}

        result = client.get(f"/api/layers/{layer_id}/settings", query_string=query_string)
        return result

    def get_dict_column_values(self, client: FlaskClient, layer_id: str, column_name: str, token: str) -> Response:
        query_string = {"token": token}

        result = client.get(f"/api/layers/{layer_id}/settings/dicts/{column_name}/values", query_string=query_string)
        return result

    def get_dicts_columns_values(self, client: FlaskClient, layer_id: str, token: str) -> Response:
        query_string = {"token": token}

        result = client.get(f"/api/layers/{layer_id}/settings/dicts/values", query_string=query_string)
        return result

    def delete_column(self, client: FlaskClient, layer_id: str, column_name: str, token: str) -> Response:
        query_string = {"token": token}
        data = {"column_name": column_name}

        result = client.delete(f"/api/layers/{layer_id}/settings", data=json.dumps(data), query_string=query_string)
        return result

    def set_dict_column_values(self, client: FlaskClient, layer_id: str, column_name: str, values: List[Any], token: str) -> Response:
        query_string = {"token": token}
        data = {"data": values}

        result = client.put(f"/api/layers/{layer_id}/settings/dicts/{column_name}/values", data=json.dumps(data), query_string=query_string)
        return result

    def test_settings_get_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.get(f'/api/layers/{lid}/settings?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['settings']['id'] == lid
        assert len(r.json['settings']['columns'].keys()) == 31

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
        assert len(r.json['settings']['columns'].keys()) == 30

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
        assert len(r.json['settings']['columns'].keys()) == 32
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

    def test_settings_change_name_styles_bug_1(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        new_column = {
            "layer_name": "test"
        }
        r = client.post(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps(new_column))
        new_lid = r.json['settings']
        r = client.get(f'/api/layers/{lid}/settings?token={token}')
        """
        Bug description:
        401 - TypeError: 'NoneType' object is not subscriptable
        """
        r = client.get(f'/api/layers/{new_lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['fill-color'] == '255,255,255,0.4'
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '2'

    def test_settings_change_name_styles_bug_2(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test1'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid2 = r.json['layers']['id']
        new_column = {
            "layer_name": "x"
        }
        r = client.post(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps(new_column))
        """
        Bug description:
        401 - TypeError: 'NoneType' object is not subscriptable
        """
        r = client.get(f'/api/layers/{lid2}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['renderer'] == 'single'
        assert r.json['style']['type'] == 'point'
        assert r.json['style']['fill-color'] == '255,255,255,0.4'
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '1'
        assert r.json['style']['width'] == '2'

    def test_create_dict_column(self, client: FlaskClient):
        token = self.get_token(client)
        column_name = "column"
        column_data = {"column_name": column_name, "column_type": "dict", "values": ["value1", "value2"]}

        layer_id = self.add_geojson_prg(client, token)

        create_result = self.post_create_column(client, layer_id, column_data, token)

        assert create_result.status_code == 200
        assert create_result.json["settings"] == f"{column_name} added"

    def test_get_dict_column(self, client: FlaskClient):
        token = self.get_token(client)
        column_name = "column"
        column_data = {"column_name": column_name, "column_type": "dict", "values": ["value1", "value2"]}

        layer_id = self.add_geojson_prg(client, token)

        self.post_create_column(client, layer_id, column_data, token)

        get_result = self.get_columns(client, layer_id, token)

        actual_columns = get_result.json["settings"]["columns"]
        assert column_name in actual_columns.keys()
        assert actual_columns[column_name] == "dict"

    def test_get_dict_values(self, client: FlaskClient):
        token = self.get_token(client)
        column_name = "column"
        column_values = ["value1", "value2"]
        column_data = {"column_name": column_name, "column_type": "dict", "values": column_values}

        layer_id = self.add_geojson_prg(client, token)

        self.post_create_column(client, layer_id, column_data, token)

        result = self.get_dict_column_values(client, layer_id, column_name, token)

        assert result.status_code == 200
        assert result.json["data"] == column_values

    def test_get_all_dicts_values(self, client: FlaskClient):
        token = self.get_token(client)

        column_1_name = "column1"
        column_1_values = ["value1", "value2"]
        column_1_data = {"column_name": column_1_name, "column_type": "dict", "values": column_1_values}

        column_2_name = "column2"
        column_2_values = ["value3", "value4"]
        column_2_data = {"column_name": column_2_name, "column_type": "dict", "values": column_2_values}

        layer_id = self.add_geojson_prg(client, token)

        self.post_create_column(client, layer_id, column_1_data, token)
        self.post_create_column(client, layer_id, column_2_data, token)


        result = self.get_dicts_columns_values(client, layer_id, token)

        expected_data = [
            {
                "column_name": column_1_name,
                "values": column_1_values
            },
            {
                "column_name": column_2_name,
                "values": column_2_values
            }
        ]

        assert result.status_code == 200
        assert result.json["data"] == expected_data

    def test_set_dict_values(self, client: FlaskClient):
        token = self.get_token(client)
        column_name = "column"
        column_values = ["value1", "value2"]
        column_data = {"column_name": column_name, "column_type": "dict", "values": column_values}

        layer_id = self.add_geojson_prg(client, token)

        self.post_create_column(client, layer_id, column_data, token)

        self.get_dict_column_values(client, layer_id, column_name, token)

        new_values = ["value3", "value4"]
        self.set_dict_column_values(client, layer_id, column_name, new_values, token)

        result = self.get_dict_column_values(client, layer_id, column_name, token)

        assert result.status_code == 200
        assert result.json["data"] == new_values

    def test_delete_dict_column(self, client: FlaskClient):
        token = self.get_token(client)
        column_name = "column"
        column_data = {"column_name": column_name, "column_type": "dict", "values": ["value1", "value2"]}

        layer_id = self.add_geojson_prg(client, token)

        self.post_create_column(client, layer_id, column_data, token)
        delete_result = self.delete_column(client, layer_id, column_name, token)

        assert delete_result.status_code == 200
        assert delete_result.json["settings"] == f"{column_name} deleted"

        get_result = self.get_columns(client, layer_id, token)

        actual_columns = get_result.json["settings"]["columns"]
        assert column_name not in actual_columns.keys()


@pytest.mark.styles
class TestLayersStyles(BaseTest):

    def test_styles_get_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        # Polygon single style
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['renderer'] == 'single'
        assert r.json['style']['type'] == 'polygon'
        assert r.json['style']['fill-color'] == '255,255,255,0.4'
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '2'
        assert r.json['style']['labels'] == []
        # Point single style
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test1'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['renderer'] == 'single'
        assert r.json['style']['type'] == 'point'
        assert r.json['style']['fill-color'] == '255,255,255,0.4'
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '1'
        assert r.json['style']['width'] == '2'
        assert r.json['style']['labels'] == []
        # Line single style
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_lines.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_lines.geojson'),
            'name': 'test2'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['renderer'] == 'single'
        assert r.json['style']['type'] == 'line'
        assert r.json['style']['stroke-color'] == '51,153,204,1'
        assert r.json['style']['stroke-width'] == '2'
        assert r.json['style']['labels'] == []

    def test_styles_put_correct_single_point(self, client):
        # Single Point
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test1'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        default_style = {
            'labels': [],
            'renderer': 'single',
            'type': 'point',
            'fill-color': '0,0,0,1',
            'stroke-color': '0,0,0,1',
            'stroke-width': '5',
            'width': '10'
        }
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        # Single Point Triangle
        default_style['type'] = 'triangle'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        assert r.json['style']['type'] == 'triangle'
        # Single Point Square
        default_style['type'] = 'square'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        assert r.json['style']['type'] == 'square'
        # Invalid
        default_style['type'] = 'circle'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 400
        assert r.json['error'] == 'invalid type'

    def test_styles_put_correct_single_line(self, client):
        # Single Line
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_lines.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_lines.geojson'),
            'name': 'test1'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        default_style = {
            'labels': [],
            'renderer': 'single',
            'type': 'line',
            'stroke-color': '0,0,0,1',
            'stroke-width': '5'
        }
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        # Single Line Dashed
        default_style['type'] = 'dashed'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        assert r.json['style']['type'] == 'dashed'
        # Single Point Dotted
        default_style['type'] = 'dotted'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        assert r.json['style']['type'] == 'dotted'
        # Invalid
        default_style['type'] = 'empty'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 400
        assert r.json['error'] == 'invalid type'

    def test_styles_put_correct_single_polygon(self, client):
        # Single Line
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct.geojson'),
            'name': 'test1'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        default_style = {
            'labels': [],
            'renderer': 'single',
            'type': 'polygon',
            'fill-color': '0,0,0,1',
            'stroke-color': '0,0,0,1',
            'stroke-width': '5'
        }
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        # Invalid
        default_style['type'] = 'empty'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 400
        assert r.json['error'] == 'invalid type'

    def test_styles_put_correct_categorized_point(self, client):
        # Categorized Point
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_points.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct_points.geojson'),
            'name': 'test1'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        attr = 'category'
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}/categories/{attr}?token={token}')
        categories = r.json['categories']
        categorized_style = {
            'labels': [],
            'renderer': 'categorized',
            'attribute': attr,
            'categories': categories
        }
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(categorized_style))
        assert r.status_code == 200
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['renderer'] == 'categorized'
        assert r.json['style']['attribute'] == attr
        assert len(r.json['style']['categories']) == 2
        # Random color
        assert r.json['style']['categories'][0]['stroke-color'] != r.json['style']['categories'][1]['stroke-color']

    def test_styles_put_correct_categorized_line(self, client):
        # Categorized Point
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'RL-48.dbf'), 'rb').read())), 'RL-48.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'RL-48.prj'), 'rb').read())), 'RL-48.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'RL-48.shp'), 'rb').read())), 'RL-48.shp'),
            'file[3]': (BytesIO((open(os.path.join(path, 'RL-48.shx'), 'rb').read())), 'RL-48.shx'),
            'file[4]': (BytesIO((open(os.path.join(path, 'RL-48.cpg'), 'rb').read())), 'RL-48.cpg'),
            'file[5]': (BytesIO((open(os.path.join(path, 'RL-48.qpj'), 'rb').read())), 'RL-48.qpj'),
            'name': 'RL-48',
            'epsg': '2180'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        attr = '06_POW'
        lid = r.json['layers']['id']
        r = client.get(f'/api/layers/{lid}/categories/{attr}?token={token}')
        categories = r.json['categories']
        categorized_style = {
            'labels': [],
            'renderer': 'categorized',
            'attribute': attr,
            'categories': categories
        }
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(categorized_style))
        assert r.status_code == 200
        r = client.get(f'/api/layers/{lid}/style?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['style']['renderer'] == 'categorized'
        assert r.json['style']['attribute'] == attr
        assert len(r.json['style']['categories']) == 14
        # Random color
        assert r.json['style']['categories'][0]['stroke-color'] != r.json['style']['categories'][1]['stroke-color']

    def test_styles_put_labels(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        # Empty labels
        default_style = {
            'labels': [],
            'renderer': 'single',
            'type': 'polygon',
            'fill-color': '0,0,0,1',
            'stroke-color': '0,0,0,1',
            'stroke-width': '5'
        }
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        assert r.json['style']['labels'] == []
        # Correct labels
        default_style['labels'] = ['JPT_SJR_KO', 'Shape_Leng']
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 200
        assert r.json['style']['labels'] == default_style['labels']
        # Invalid labels
        default_style['labels'] = ['test', 'Shape_Leng']
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 400
        assert r.json['error'] == 'invalid labels - column test not exists'
        # Invalid labels type
        default_style['labels'] = 'test'
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 400
        assert r.json['error'] == 'invalid labels type'
        default_style['labels'] = 1
        r = client.put(f'/api/layers/{lid}/style?token={token}',
                       data=json.dumps(default_style))
        assert r.status_code == 400
        assert r.json['error'] == 'invalid labels type'


@pytest.mark.export
class TestLayersExport(BaseTest):

    def test_export_geojson(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = self.add_feature_to_layer(client, token, lid)
        data = {
            'filter_ids': [fid]
        }
        r = client.post(
            f'/api/layers/{lid}/export/geojson?token={token}', data=json.dumps(data))
        data = json.loads(BytesIO(r.data).read())
        assert len(data['features']) == 1
        r = client.post(
            f'/api/layers/{lid}/export/geojson?token={token}', data=json.dumps({}))
        data = json.loads(BytesIO(r.data).read())
        assert len(data['features']) == 2


@pytest.mark.mvt
class TestMVT(BaseTest):

    def test_correct_geojson(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct.geojson'),
            'name': 'correct'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        lid = r.json['layers']['id']
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'correct'
        lid = r.json['layers']['id']
        r = client.get(f'/api/mvt/{lid}/10/562/336?token={token}')
        assert r.status_code == 200

    def test_RL_77(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'layers')
        file_request = {
            'file[0]': (BytesIO((open(os.path.join(path, 'RL-77.dbf'), 'rb').read())), 'RL-77.dbf'),
            'file[1]': (BytesIO((open(os.path.join(path, 'RL-77.prj'), 'rb').read())), 'RL-77.prj'),
            'file[2]': (BytesIO((open(os.path.join(path, 'RL-77.shx'), 'rb').read())), 'RL-77.shx'),
            'file[3]': (BytesIO((open(os.path.join(path, 'RL-77.shp'), 'rb').read())), 'RL-77.shp'),
            'name': 'RL-77',
            'encoding': 'cp1250'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 10
        assert r.json['layers']['name'] == 'RL-77'
        lid = r.json['layers']['id']
        r = client.get(f'/api/mvt/{lid}/17/73814/44015?token={token}')
        assert r.status_code == 200

