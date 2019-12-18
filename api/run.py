#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.create import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=app.config['APP_PORT'], threaded=True)
else:
    app = create_app('production')
