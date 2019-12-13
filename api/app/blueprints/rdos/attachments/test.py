#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.tests.utils import BaseTest
import pytest


@pytest.mark.attachments
class TestAttachments(BaseTest):

    def test_attachments_get_correct(self, client):
        token = self.get_token(client)
        lid = self.add_geojson_prg(client, token)
        r = client.get(f'/api/layers/{lid}/attachments?token={token}')
        assert r.status_code == 200
        assert r.json
        # Testowo zainicjalizowane są 3 załącnziki z dwóch grup + publiczne
        assert len(r.json['attachments']) == 2
        assert 'public' in [a['group'] for a in r.json['attachments']]
        assert 'default' in [a['group'] for a in r.json['attachments']]
        assert 'private' not in [a['group'] for a in r.json['attachments']]
