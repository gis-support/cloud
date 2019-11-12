#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from io import BytesIO
import uuid

TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__))

class BaseTest:

    def register(self, client):
        user = str(uuid.uuid4())
        password = str(uuid.uuid4())
        r = client.post('/api/register', data=json.dumps({"user": user, "password": password}))
        assert r.status_code == 201
        assert r.json
        assert r.json['register'] == 'user created'
        return user, password
    
    def get_token(self, client):
        user, password = self.register(client)
        r = client.post('/api/login', data=json.dumps({"user": user, "password": password}))
        assert r.status_code == 200
        assert r.json
        assert r.json['token']
        assert len(r.json['token']) > 10
        return r.json['token']
    
    def add_geojson_prg(self, client, token):
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct.geojson')
        file_request = {
            'file': (BytesIO(open(path, 'rb').read()), 'correct.geojson'),
            'name': 'wojewodztwa'
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request, follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == 'wojewodztwa'