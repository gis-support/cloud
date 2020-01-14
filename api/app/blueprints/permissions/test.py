#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest, TEST_DATA_DIR
import json
import pytest
import os
from io import BytesIO


@pytest.mark.permissions
class TestPermissions(BaseTest):

    def test_permissions_all(self, client):
        test_user = self.get_token(client)
        token_admin = self.get_token(client)
        user, password = self.create_user(client)
        # Create 4 layers
        # First only for admin user
        lid1 = self.add_geojson_prg(client, token_admin)
        # Second for normal user read only
        lid2 = self.add_geojson_prg(client, token_admin, name='wojewodztwa2')
        r = client.put(f'/api/permissions/{lid2}?token={token_admin}',
                       data=json.dumps({'user': user, 'permission': 'read'}))
        # Third for normal user write permission
        lid3 = self.add_geojson_prg(client, token_admin, name='wojewodztwa3')
        r = client.put(f'/api/permissions/{lid3}?token={token_admin}',
                       data=json.dumps({'user': user, 'permission': 'write'}))
        # Fourth only for normal user
        token = self.get_token(client, user=user, password=password)
        lid4 = self.add_geojson_prg(client, token, name='wojewodztwa4')
        # Get all permissions
        r = client.get(f'/api/permissions?token={token_admin}')
        assert r.status_code == 200
        assert r.json
        # Rules
        # There are three layers for admin user
        assert len(r.json['permissions']) == 3
        # There are three users so every layer has three users (more if prod db is up)
        for perm in r.json['permissions']:
            assert len(perm['users']) > 2
            # First only has write to admin
            if perm['id'] == lid1:
                counter = 0
                for user in perm['users']:
                    if perm['users'][user] == 'write':
                        counter += 1
                assert counter == 1
            # Second read only + write:
            if perm['id'] == lid2:
                counter_w = 0
                counter_r = 0
                for user in perm['users']:
                    if perm['users'][user] == 'write':
                        counter_w += 1
                    if perm['users'][user] == 'read':
                        counter_r += 1
                assert counter_w == 1
                assert counter_r == 1
            # Third is double write
            if perm['id'] == lid3:
                counter = 0
                for user in perm['users']:
                    if perm['users'][user] == 'write':
                        counter += 1
                assert counter == 2
            # Fourth only one for user
            if perm['id'] == lid4:
                counter = 0
                write_user = ""
                for user in perm['users']:
                    if perm['users'][user] == 'write':
                        counter += 1
                        write_user = user
                assert counter == 1
                assert write_user == user

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
        user, password = self.create_user(client)
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
        r = client.post('/api/layers/{}/features?token={}'.format(lid, token),
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
        r = client.post('/api/layers/{}/features?token={}'.format(lid, token),
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
        user, password = self.create_user(client)
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
        r = client.post('/api/layers/{}/features?token={}'.format(lid, token),
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
        r = client.post('/api/layers/{}/features?token={}'.format(lid, token),
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
