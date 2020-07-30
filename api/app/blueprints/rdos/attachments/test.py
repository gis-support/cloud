#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest
import pytest
import json
import os


@pytest.mark.attachments
class TestAttachments(BaseTest):

    def test_attachments_post_correct_public(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        aid = self.add_attachment_to_feature(
            client, token, lid, fid, public=True)
        r = client.get(
            f'/api/layers/{lid}/features/{fid}/attachments?token={token}')
        assert r.status_code == 200
        assert r.json
        default_group = os.environ.get('DEFAULT_GROUP')
        assert len(r.json['attachments'][default_group]) == 1

    def test_attachments_post_correct_group(self, client):
        token = self.get_token(client, default_group=False)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        aid = self.add_attachment_to_feature(
            client, token, lid, fid, public=False)
        r = client.get(
            f'/api/layers/{lid}/features/{fid}/attachments?token={token}')
        assert r.status_code == 200
        assert r.json
        default_group = os.environ.get('DEFAULT_GROUP')
        not_default_group = [
            i for i in r.json['attachments'].keys() if i != default_group][0]
        assert len(r.json['attachments'][default_group]) == 0
        assert len(r.json['attachments'][not_default_group]) == 1

    def test_attachments_change_layer_name(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        aid = self.add_attachment_to_feature(client, token, lid, fid)
        new_layer_name = {
            "layer_name": "test"
        }
        r = client.post(
            f'/api/layers/{lid}/settings?token={token}', data=json.dumps(new_layer_name))
        new_lid = r.json['settings']
        r = client.get(
            f'/api/layers/{new_lid}/features/{fid}/attachments?token={token}')
        assert r.status_code == 200
        assert r.json
        default_group = os.environ.get('DEFAULT_GROUP')
        assert len(r.json['attachments'][default_group]) == 1

    def test_attachments_delete_public(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        fid = 1
        aid = self.add_attachment_to_feature(
            client, token, lid, fid, public=True)
        r = client.delete(
            f'/api/layers/{lid}/features/{fid}/attachments/1?token={token}')
        assert r.status_code == 200
        assert r.json
        assert r.json['aid'] == 1
        r = client.get(
            f'/api/layers/{lid}/features/{fid}/attachments?token={token}')
        assert r.status_code == 200
        assert r.json
        default_group = os.environ.get('DEFAULT_GROUP')
        assert len(r.json['attachments'][default_group]) == 0

    def test_delete_attachment_by_not_owner(self, client):
        admin = self.get_token(client, admin=True)
        # Nowy użytkownik - właściciel warstwy
        owner_user, owner_user_pass = self.create_user(client)
        owner_user_token = self.get_token(client, owner_user, owner_user_pass)
        # Przypisanie użytkownika do grupy 'test'
        self.create_or_get_group_and_assign_user(client, owner_user)
        # Dodanie kolejnego użytkownika
        not_owner_user, not_owner_user_pass = self.create_user(client)
        not_owner_user_token = self.get_token(client, not_owner_user, not_owner_user_pass)
        # Przypisanie nowego użytkownika do grupy test
        self.create_or_get_group_and_assign_user(client, not_owner_user)
        r = client.get(f'/api/users?token={admin}')
        # Dodanie warstwy przez nowego użytkownika
        lid = self.add_geojson_prg(client, owner_user_token)
        fid = 1
        # Dodanie załącznika
        aid = self.add_attachment_to_feature(client, owner_user_token, lid, fid, public=False)
        r = client.get(
            f'/api/layers/{lid}/features/{fid}/attachments?token={owner_user_token}')
        assert r.status_code == 200
        assert r.json
        # Nadanie praw do odczytu warstwy
        r = client.put(f'/api/permissions/{lid}?token={owner_user_token}',
          data=json.dumps({'user': not_owner_user, 'permission': 'read'}))
        # Próba usunięcia załącznika przy prawach tylko do odczytu
        r = client.get(f'/layers?token={owner_user_token}')
        r = client.delete(
          f'/api/layers/{lid}/features/{fid}/attachments/{aid}?token={not_owner_user_token}')
        assert r.status_code == 403
        assert r.json['error'] == 'access denied, read only permission'
        # Nadanie praw do edycji i próba usunięcia
        r = client.put(f'/api/permissions/{lid}?token={owner_user_token}',
          data=json.dumps({'user': not_owner_user, 'permission': 'write'}))
        r = client.delete(
          f'/api/layers/{lid}/features/{fid}/attachments/{aid}?token={not_owner_user_token}')
        assert r.status_code == 200
        assert r.json['aid'] == aid