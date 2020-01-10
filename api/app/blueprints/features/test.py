#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest, TEST_DATA_DIR
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
