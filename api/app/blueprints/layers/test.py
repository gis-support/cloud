#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.test_data.utils import BaseTest, TEST_DATA_DIR
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
    
    def test_layers_delete_correct(self, client):
        token = self.get_token(client)
        self.add_geojson_prg(client, token)
        r = client.delete('/api/layers?token={}&name={}'.format(token, 'wojewodztwa'))
        assert r.status_code == 200
        assert r.json
        assert r.json['layers'] == 'wojewodztwa removed'