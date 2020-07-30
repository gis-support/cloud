#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from io import BytesIO
import uuid
from pathlib import Path

TEST_DATA_DIR = str(Path(Path(__file__).parent, "resources").absolute())


class BaseTest:

    DEFAULT_USER = os.environ.get('DEFAULT_USER')
    DEFAULT_PASS = os.environ.get('DEFAULT_PASS')

    def create_user(self, client, default_group=True):
        token = self.get_token(client, admin=True)
        user = str(uuid.uuid4())
        password = str(uuid.uuid4())
        data = {"user": user, "password": password}
        if not default_group:
            not_default_group = [
                i for i in os.environ['DEFAULT_GROUPS'].split(',') if i != os.environ['DEFAULT_GROUP']][0]
            data['group'] = not_default_group
        r = client.post(f'/api/users?token={token}',
                        data=json.dumps(data))
        assert r.status_code == 201
        assert r.json
        assert r.json['users'] == 'user created'
        return user, password

    def get_token(self, client, user="", password="", default_group=True, admin=False):
        if admin:
            user = self.DEFAULT_USER
            password = self.DEFAULT_PASS
        if not user and not password:
            user, password = self.create_user(
                client, default_group=default_group)
        r = client.post(
            '/api/login', data=json.dumps({"user": user, "password": password}))
        assert r.status_code == 200
        assert r.json
        assert r.json['token']
        assert len(r.json['token']) > 10
        return r.json['token']

    def add_geojson_prg(self, client, token, name='wojewodztwa'):
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct.geojson')
        file_request = {
            'file[]': (BytesIO(open(path, 'rb').read()), 'correct.geojson'),
            'name': name
        }
        r = client.post('/api/layers?token={}'.format(token), data=file_request,
                        follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['layers']['features'] == 1
        assert r.json['layers']['name'] == name
        return r.json['layers']['id']

    def add_feature_to_layer(self, client, token, lid):
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.post('/api/layers/{}/features?token={}'.format(lid, token),
                        data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 201
        assert r.json
        assert r.json['type'] == 'Feature'
        return r.json['properties']['id']

    def add_attachment_to_feature(self, client, token, lid, fid, public=True, name='test', link='https://gis-support.pl/'):
        r = client.get(
            f'/api/layers/{lid}/features/{fid}/attachments?token={token}')
        assert r.status_code == 200
        assert r.json
        default_group = os.environ.get('DEFAULT_GROUP')
        assert r.json['attachments'][default_group] == []
        new_attachment = {
            'public': public,
            'link': link,
            'name': name
        }
        r = client.post(
            f'/api/layers/{lid}/features/{fid}/attachments?token={token}', data=json.dumps(new_attachment))
        assert r.status_code == 201
        assert r.json
        return r.json['attachments']['id']

    def add_service(self, client, token, public=True):
        request = {
            'name': 'geoportal prg',
            'url': 'https://integracja.gugik.gov.pl/cgi-bin/KrajowaIntegracjaNumeracjiAdresowej',
            'layers': 'prg-adresy,prg-ulice,prg-place',
            'public': public
        }
        r = client.post(
            f'/api/services?token={token}', data=json.dumps(request))
        assert r.status_code == 201
        assert r.json
        assert r.json['services']['name'] == request['name']
        assert r.json['services']['url'] == request['url']
        assert r.json['services']['layers'] == request['layers']
        return r.json['services']['id']

    def create_or_get_group_and_assign_user(self, client, user, group='tescik'):
        token = self.get_token(client, admin=True)
        r = client.get(f'/api/users/groups?token={token}')
        if group not in r.json['groups']:
            r = client.post(
                f'/api/users/groups?token={token}', data=json.dumps({'group': group}))
            assert r.status_code == 201
            assert r.json['groups'] == 'group added'
        # Changing user assignment from default to newly created group
        # print(user, group)
        r = client.put(
            f'/api/users?token={token}', data=json.dumps({'user': user, 'group': group}))
        assert r.status_code == 200
        assert r.json['users'] == 'user assigned'