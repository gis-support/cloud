#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.test_data.utils import BaseTest, TEST_DATA_DIR
import json
import pytest

@pytest.mark.features
class TestFeatures(BaseTest):

    def test_features_get_correct(self, client):
        token = self.get_token(client)
        self.add_geojson_prg(client, token)
        r = client.get('/api/features?token={}&name={}'.format(token, 'wojewodztwa'))
        assert r.status_code == 200
        assert r.json
        assert r.json['type'] == 'FeatureCollection'
        assert len(r.json['features']) == 1

    def test_features_get_by_id_correct(self, client):
        token = self.get_token(client)
        self.add_geojson_prg(client, token)
        r = client.get('/api/features/1?token={}&name={}'.format(token, 'wojewodztwa'))
        assert r.status_code == 200
        assert r.json
        assert r.json['type'] == 'Feature'