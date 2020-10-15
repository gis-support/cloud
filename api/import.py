#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path
from io import BytesIO
from copy import deepcopy
import json
import requests

IMPORT_PATH = "/api/import/"
IMPORT_DATA_PATH = path.join(IMPORT_PATH, "dane_export")
API_USER = "admin"
API_PASS = "admin"
API_URL = "http://localhost:5001/api"


def validate_config():
    invalid = False
    layers = []
    with open(path.join(IMPORT_PATH, 'config.json'), 'r') as jf:
        data = json.load(jf)
        for lyr in data['warstwy']:
            layers.append(lyr)
            if lyr.get('kodowanie') not in ['utf-8', 'cp1250']:
                break
            for f in lyr['pliki']:
                if not path.exists(path.join(IMPORT_DATA_PATH, f)):
                    invalid = f
                    break
    return invalid, layers


def get_token():
    r = requests.post(f'{API_URL}/login',
                      json.dumps({"user": API_USER, "password": API_PASS}))
    return r.json()['token']

def clear_style(style):
    copy_style = deepcopy(style)
    if len(style['labels']) > 0:
        copy_style['labels'] = [i.upper() for i in style['labels']]
    if 'width' in style:
        copy_style['width'] = int(style['width'])
    if 'stroke-width' in style:
        copy_style['stroke-width'] = int(style['stroke-width'])
    return copy_style

def upload_layers(layers):
    token = get_token()
    for idx, lyr in enumerate(layers):
        request_body = {
            'name': lyr['nazwa'],
            'epsg': lyr['uklad'],
            'encoding': lyr['kodowanie']
        }
        files = {}
        for i, f in enumerate(lyr['pliki']):
            files[f'file[{i}]'] = (f, open(path.join(IMPORT_DATA_PATH, f), 'rb'))
        print(f"Importing {idx+1}/{len(layers)} layer...")
        try:
            r = requests.post(
                f'{API_URL}/layers?token={token}', data=request_body, files=files)
            if 'error' in r.json():
                print(f"Error: {r.json()['error']}")
            else:
                print(f"Success: {r.json()}")
                style = lyr['styl']
                r = requests.put(f'{API_URL}/layers/{r.json()["layers"]["id"]}/style?token={token}',
                                 json.dumps(style))
                if 'error' in r.json():
                    err = r.json()['error']
                    style = clear_style(style)
                    r = requests.put(f'{API_URL}/layers/{r.json()["layers"]["id"]}/style?token={token}',
                                        json.dumps(style))
                    if 'error' in r.json():
                        print(f"Error: {r.json()['error']}")
                    else:
                        print(f"Success style: {r.json()}")
                else:
                    print(f"Success style: {r.json()}")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    if not path.exists(IMPORT_PATH):
        print('Import path not exists')
    if not path.exists(IMPORT_DATA_PATH):
        print('Import data path not exists')
    if not path.exists(path.join(IMPORT_PATH, 'config.json')):
        print('Config file not exists')
    error, layers = validate_config()
    if error:
        print(f'{error} file not exists')
    upload_layers(layers)
