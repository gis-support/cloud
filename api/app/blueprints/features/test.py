#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest, TEST_DATA_DIR
from time import time
import datetime
import json
import pytest
import os


@pytest.mark.features
class TestFeatures(BaseTest):

    def test_features_get_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 200
        assert r.json
        assert r.json['type'] == 'FeatureCollection'
        assert len(r.json['features']) == 1

    def test_features_get_by_id_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        r = client.get(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 200
        assert r.json
        assert r.json['type'] == 'Feature'

    def test_features_post_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        self.add_feature_to_layer(client, token, lid)

    def test_features_put_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.get(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        base_geometry = len(r.json['geometry']['coordinates'][0][0])
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
        r = client.get(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        edited_geometry = len(r.json['geometry']['coordinates'][0][0])
        assert base_geometry > edited_geometry

    def test_features_put_geometry_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
        assert r.json
        assert r.json['type'] == 'Feature'

    def test_features_delete_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 200
        assert r.json
        assert r.json['fid'] == fid
        r = client.get(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 404
        assert r.json
        assert r.json['error'] == 'feature not exists'
        r = client.get(
            '/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 200
        assert r.json
        assert r.json['features'] == []

    def test_features_invalid_type(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        r = client.get(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        base_geometry = len(r.json['geometry']['coordinates'][0][0])
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        feature = json.loads(open(path).read())
        # Shape_Leng need to be float or int, check string
        feature['properties']['Shape_Leng'] = "e"
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=json.dumps(feature), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 400
        r = client.get(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        edited_geometry = len(r.json['geometry']['coordinates'][0][0])
        assert base_geometry == edited_geometry
        # Shape_Leng need to be float or int, check int
        feature['properties']['Shape_Leng'] = 1
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=json.dumps(feature), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
        # Shape_Leng need to be float, check float
        feature['properties']['Shape_Leng'] = 1.0
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=json.dumps(feature), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
        # WERSJA_OD need to be timestamp, check string
        feature['properties']['WERSJA_OD'] = "e"
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=json.dumps(feature), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 400
        #  WERSJA_OD need to be datetime string, check int
        feature['properties']['WERSJA_OD'] = int(time())
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=json.dumps(feature), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
        #  WERSJA_OD need to be datetime string, check float
        feature['properties']['WERSJA_OD'] = time()
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=json.dumps(feature), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
