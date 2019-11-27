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
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'wojewodztwa'

    def test_features_delete_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 200
        assert r.json
        assert r.json['layers']['features'] == 0
        assert r.json['layers']['name'] == 'wojewodztwa'
