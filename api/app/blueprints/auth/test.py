#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest, TEST_DATA_DIR
from io import BytesIO
import json
import pytest
import os


@pytest.mark.auth
class TestAuth(BaseTest):

    def test_users_correct(self, client):
        self.create_user(client)

    def test_users_duplicate(self, client):
        user, password = self.create_user(client)
        token = self.get_token(client, admin=True)
        r = client.post(f'/api/users?token={token}',
                        data=json.dumps({'user': user, 'password': password}))
        assert r.status_code == 409
        assert r.json
        assert r.json['error'] == 'user exists'

    def test_login_correct(self, client):
        token = self.get_token(client)
        assert len(token) > 0

    def test_login_invalid(self, client):
        self.create_user(client)
        r = client.post(
            '/api/login', data=json.dumps({'user': 'test', 'password': '?'}))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'invalid credentials'

    def test_login_user_password_required(self, client):
        self.create_user(client)
        r = client.post(
            '/api/login', data=json.dumps({'test': 'test', 'password': '?'}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'user required'
        r = client.post(
            '/api/login', data=json.dumps({'user': 'test', 'test': '?'}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'password required'

    def test_users_get_correct(self, client):
        token = self.get_token(client, admin=True)
        r = client.get(f'/api/users?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['users']
        assert r.json['users'][os.environ['DEFAULT_USER']
                               ] == os.environ.get('DEFAULT_GROUP')

    def test_delete_user_by_admin(self, client):
        token = self.get_token(client, admin=True)
        user_to_delete = 'test'
        client.post(
            f'/api/users?token={token}', data=json.dumps({'user': user_to_delete, 'password': 'test'}))
        r = client.post(
            '/api/login', data=json.dumps({'user': user_to_delete, 'password': 'test'}))
        assert r.status_code == 200
        assert r.json
        assert r.json['token']
        r = client.delete(
            f'/api/users?token={token}', data=json.dumps({'user': user_to_delete}))
        assert r.status_code == 200
        assert r.json
        assert r.json['users'] == 'user deleted'
        r = client.post(
            '/api/login', data=json.dumps({'user': user_to_delete, 'password': 'test'}))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'invalid credentials'

    def test_delete_user_by_user(self, client):
        user_to_delete, _ = self.create_user(client)
        user, password = self.create_user(client)
        r = client.post(
            '/api/login', data=json.dumps({'user': user, 'password': password}))
        assert r.status_code == 200
        assert r.json
        token = r.json['token']
        r = client.delete(
            f'/api/users?token={token}', data=json.dumps({'user': user_to_delete}))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'permission denied'

    def test_delete_admin(self, client):
        token = self.get_token(client, admin=True)
        user_to_delete = 'admin'
        r = client.delete(
            f'/api/users?token={token}', data=json.dumps({'user': user_to_delete}))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'permission denied'


@pytest.mark.auth
class TestGroups(BaseTest):

    def test_groups_get_correct(self, client):
        token = self.get_token(client, admin=True)
        r = client.get(f'/api/users/groups?token={token}')
        assert r.status_code == 200
        assert r.json
        assert len(r.json['groups']) == len(
            os.environ.get('DEFAULT_GROUPS', '').split(','))

    def test_groups_post_correct(self, client):
        token = self.get_token(client, admin=True)
        r = client.post(
            f'/api/users/groups?token={token}', data=json.dumps({'group': 'test'}))
        assert r.status_code == 201
        assert r.json
        assert r.json['groups'] == 'group added'
        r = client.get(f'/api/users/groups?token={token}')
        assert r.status_code == 200
        assert r.json
        assert len(r.json['groups']) == (len(
            os.environ.get('DEFAULT_GROUPS', '').split(',')) + 1)
        assert 'test' in r.json['groups']

    def test_groups_delete_correct(self, client):
        token = self.get_token(client, admin=True)
        client.post(
            f'/api/users/groups?token={token}', data=json.dumps({'group': 'test'}))
        r = client.delete(
            f'/api/users/groups?token={token}', data=json.dumps({'group': 'test'}))
        assert r.status_code == 200
        assert r.json
        assert r.json['groups'] == 'group deleted'
        r = client.get(f'/api/users/groups?token={token}')
        assert r.status_code == 200
        assert r.json
        assert len(r.json['groups']) == len(
            os.environ.get('DEFAULT_GROUPS', '').split(','))
        assert 'test' not in r.json['groups']

    def test_groups_exists_post(self, client):
        default_group = os.environ.get('DEFAULT_GROUP')
        token = self.get_token(client, admin=True)
        r = client.post(
            f'/api/users/groups?token={token}', data=json.dumps({'group': default_group}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'group exists'

    def test_groups_not_exists_delete(self, client):
        default_group = os.environ.get('DEFAULT_GROUP')
        token = self.get_token(client, admin=True)
        r = client.delete(
            f'/api/users/groups?token={token}', data=json.dumps({'group': 'test'}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'group not exists'

    def test_groups_assign_user_correct(self, client):
        token = self.get_token(client, admin=True)
        user, _ = self.create_user(client)
        client.post(
            f'/api/users/groups?token={token}', data=json.dumps({'group': 'test'}))
        r = client.put(
            f'/api/users?token={token}', data=json.dumps({'user': user, 'group': 'test'}))
        assert r.status_code == 200
        assert r.json
        assert r.json['users'] == 'user assigned'

    def test_groups_assign_user_invalid_user(self, client):
        token = self.get_token(client, admin=True)
        client.post(
            f'/api/users/groups?token={token}', data=json.dumps({'group': 'test'}))
        r = client.put(
            f'/api/users?token={token}', data=json.dumps({'user': 'test', 'group': 'test'}))
        assert r.status_code == 409
        assert r.json
        assert r.json['error'] == 'user not exists'

    def test_groups_assign_user_invalid_group(self, client):
        token = self.get_token(client, admin=True)
        user, _ = self.create_user(client)
        r = client.put(
            f'/api/users?token={token}', data=json.dumps({'user': user, 'group': 'test'}))
        assert r.status_code == 409
        assert r.json
        assert r.json['error'] == 'group not exists'

    def test_groups_restricted_group_delete(self, client):
        default_group = os.environ.get('DEFAULT_GROUP')
        token = self.get_token(client, admin=True)
        r = client.delete(
            f'/api/users/groups?token={token}', data=json.dumps({'group': os.environ['DEFAULT_GROUP']}))
        assert r.status_code == 400
        assert r.json
        assert r.json['error'] == 'group restricted'


@pytest.mark.auth
class TestLogo(BaseTest):

    def test_get_logo(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'images', 'logo.png')
        r = client.get('/api/logo')
        assert r.get_data() == open(path, 'rb').read()

    def test_post_logo(self, client):
        token = self.get_token(client)
        path = os.path.join(TEST_DATA_DIR, 'images', 'logo.png')
        file_request = {
            'file': (BytesIO(open(path, 'rb').read()), 'logo.png'),
        }
        r = client.post('/api/logo?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.get_data() == open(path, 'rb').read()
