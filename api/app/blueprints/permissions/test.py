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
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        token = self.get_token(client)
        r = client.delete(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'

    def test_permssion_read_only(self, client):
        # Nowy użytkownik
        token_admin = self.get_token(client)
        # Nowa warstwa dla użytkownika
        lid = self.add_geojson_prg(client, token_admin)
        # Dodanie nowego użytkownika
        user, password = self.register(client)
        # Nadanie uprawnień nowemu użytkonikowi
        r = client.put(f'/api/permissions/{lid}?token={token_admin}',
                        data=json.dumps({'user': user, 'permission': 'read'}))
        # Zalogowanie na nowego użytkownika
        token = self.get_token(client, user=user, password=password)
        # Próba usunięcia warstwy
        r = client.delete(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, not an owner'
        # Próba dodania ficzera
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.post('/api/layers/{}?token={}'.format(lid, token),
                        data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, read only permission'
        # Próba usunięcia ficzera
        fid = 1
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, read only permission'
        # Próba edycji ficzera
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied, read only permission'
        # Pobranie nowej warstwy
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 200
        # Zabranie praw użytkownikowi
        r = client.put(f'/api/permissions/{lid}?token={token_admin}',
                        data=json.dumps({'user': user, 'permission': ''}))
        # Pobranie poprzedniej warstwy
        r = client.get('/api/layers/{}?token={}'.format(lid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Ponowna próba usunięcia warstwy
        r = client.delete(f'/api/layers/{lid}?token={token}')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Ponowna próba dodania ficzera
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.post('/api/layers/{}?token={}'.format(lid, token),
                        data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Ponowna próba usunięcia ficzera
        fid = 1
        r = client.delete(
            '/api/layers/{}/features/{}?token={}'.format(lid, fid, token))
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
        # Ponowna próba edycji ficzera
        fid = 1
        path = os.path.join(TEST_DATA_DIR, 'layers', 'correct_feature.json')
        r = client.put('/api/layers/{}/features/{}?token={}'.format(lid, fid, token),
                       data=open(path), follow_redirects=True, content_type='multipart/form-data')
        assert r.status_code == 403
        assert r.json
        assert r.json['error'] == 'access denied'
