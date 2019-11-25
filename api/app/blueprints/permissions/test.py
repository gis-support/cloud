#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest, TEST_DATA_DIR
import json
import pytest
import os
from io import BytesIO


@pytest.mark.permissions
class TestPermissions(BaseTest):

    def test_permission_denied(self, client):
        # Smoke test - visible of new layer for other users
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        token = self.get_token(client)
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'

    def test_permssion_read_only(self, client):
        # New admin user
        token_admin = self.get_token(client)
        # New layer
        lid = self.add_geojson_prg(client, token_admin)
        # New normal user
        user, password = self.register(client)
        # Grant permission for normal user by admin
        r = client.put(f'/api/permissions/{lid}?token={token_admin}',
                        data=json.dumps({'user': user, 'permission': 'read'}))
        # Normal user log in
        token = self.get_token(client, user=user, password=password)
        # Try to delete layer with different owner
        r = client.delete(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, not an owner'
        # Try to add feature with read only permission
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.post('/api/layers/{}?token={}'.format(lid, token),
                        data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, read only permission'
        # Try to delete feature with read only permission
        fid = 1
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, read only permission'
        # Try to edit feature with read only permission
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, read only permission'
        # Get layer
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 200
        # Revoke permissions for normal user by admin
        r = client.put(f'/api/permissions/{lid}?token={token_admin}',
                        data=json.dumps({'user': user, 'permission': ''}))
        # Try to get layer
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to delete layer with no permissions
        r = client.delete(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to add feature with no permissions
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.post('/api/layers/{}?token={}'.format(lid, token),
                        data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to delete feature with no permissions
        fid = 1
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to edit feature with no permissions
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'

    def test_permssion_write(self, client):
        # New admin user
        token_admin = self.get_token(client)
        # New layer
        lid = self.add_geojson_prg(client, token_admin)
        # New normal user
        user, password = self.register(client)
        # Grant permission for normal user by admin
        r = client.put(f'/api/permissions/{lid}?token={token_admin}',
                        data=json.dumps({'user': user, 'permission': 'write'}))
        # Normal user log in
        token = self.get_token(client, user=user, password=password)
        # Try to delete layer with different owner
        r = client.delete(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, not an owner'
        # Try to add feature with read only permission
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.post('/api/layers/{}?token={}'.format(lid, token),
                        data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        # Try to delete feature with read only permission
        fid = 2
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 200
        # Try to edit feature with read only permission
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 200
        # Get layer
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 200
        # Revoke permissions for normal user by admin
        r = client.put(f'/api/permissions/{lid}?token={token_admin}',
                        data=json.dumps({'user': user, 'permission': ''}))
        # Try to get layer
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to delete layer with no permissions
        r = client.delete(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to add feature with no permissions
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.post('/api/layers/{}?token={}'.format(lid, token),
                        data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to delete feature with no permissions
        fid = 1
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Try to edit feature with no permissions
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
