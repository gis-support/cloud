#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path
from io import BytesIO
import json
import requests

IMPORT_PATH = "/api/import/"
API_USER = "admin"
API_PASS = "admin"
API_URL = "https://cloud.gis.support/api"


def validate_config():
    invalid = False
    layers = []
    with open(path.join(IMPORT_PATH, 'config.json'), 'r') as jf:
        data = json.load(jf)
        for lyr in data['warstwy']:
            layers.append(lyr)
            for f in lyr['pliki']:
                if not path.exists(path.join(IMPORT_PATH, f)):
                    invalid = f
                    break
    return invalid, layers


def get_token():
    r = requests.post(f'{API_URL}/login',
                      json.dumps({"user": API_USER, "password": API_PASS}))
    return r.json()['token']


def upload_layers(layers):
    token = get_token()
    for idx, lyr in enumerate(layers):
        request_body = {
            'name': lyr['nazwa'],
            'epsg': lyr['uklad']
        }
        files = {}
        for i, f in enumerate(lyr['pliki']):
            files[f'file[{i}]'] = (f, open(path.join(IMPORT_PATH, f), 'rb'))
        print(f"Importing {idx+1}/{len(layers)} layer...")
        try:
            r = requests.post(
                f'{API_URL}/layers?token={token}', data=request_body, files=files)
            if 'error' in r.json():
                print(f"Error: {r.json()['error']}")
            else:
                print(f"Success: {r.json()}")
        except:
            print('Error on server side')


if __name__ == '__main__':
    if not path.exists(IMPORT_PATH):
        print('Import path not exists')
    if not path.exists(path.join(IMPORT_PATH, 'config.json')):
        print('Config file not exists')
    error, layers = validate_config()
    if error:
        print(f'{error} file not exists')
    upload_layers(layers)
