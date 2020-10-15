#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path
from io import BytesIO
import json
import requests

IMPORT_PATH = "/api/import/"
API_USER = "admin"
API_PASS = "admin"
API_URL = "http://localhost:5001/api"


def validate_config():
    objects = []
    with open(path.join(IMPORT_PATH, 'zalaczniki.json'), 'r') as jf:
        data = json.load(jf)
        for obj in data['attachments']:
            objects.append(obj)
            for attachment in obj['attachment']:
                pass
    return objects


def get_token():
    r = requests.post(f'{API_URL}/login',
                      json.dumps({"user": API_USER, "password": API_PASS}))
    return r.json()['token']


def upload_attachments(objects):
    token = get_token()
    for idx, obj in enumerate(objects):
        attachments = obj['attachment']
        group = obj['group']
        layer_id = obj['layer']
        object_id = obj['_id']
        r = requests.get(f'{API_URL}/layers/{layer_id}?token={token}')
        features = r.json()['features']
        try:
            feature_object_id = [
                i for i in features if i['properties']['_id'] == object_id][0]['properties']['_id']
        except:
            print(f'Fail: {layer_id}/{object_id}')
            continue
        url = f'{API_URL}/layers/{layer_id}/features/{feature_object_id}/attachments?token={token}'
        r = requests.get(url)
        for attachment in r.json()['attachments']['default']:
            requests.delete(
                f"{API_URL}/layers/{layer_id}/features/{feature_object_id}/attachments/{attachment['id']}?token={token}")
        for idx, link in enumerate(attachments):
            request_body = {
                'public': False if group == 'private' else True,
                'link': link,
                'name': f'Załącznik {idx + 1}'
            }
            r = requests.post(url, json=request_body)
            print(f'Success: {layer_id}/{feature_object_id}')
        """ r = requests.get(url)
        print(r.json()) """


if __name__ == '__main__':
    if not path.exists(IMPORT_PATH):
        print('Import path not exists')
    if not path.exists(path.join(IMPORT_PATH, 'zalaczniki.json')):
        print('Config file not exists')
    objects = validate_config()
    upload_attachments(objects)
