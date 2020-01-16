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
