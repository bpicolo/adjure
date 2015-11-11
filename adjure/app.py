# -*- coding: utf-8 -*-
import argparse
import logging

import staticconf
from flask import Flask
from logstash_formatter import LogstashFormatterV1

from adjure.routes.auth import auth_page


def register_app_config(config_path):
    staticconf.YamlConfiguration(config_path, namespace='adjure')
    return staticconf.NamespaceReaders('adjure')


def setup_logging(app, config):
    log_path = config.read('logging.log_path', default=None)
    if not log_path:
        return

    handler = logging.FileHandler(log_path)
    handler.setFormatter(LogstashFormatterV1())
    app.logger.addHandler(handler)


def build_app():
    app = Flask(__name__)
    app.register_blueprint(auth_page)
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the adjure server')
    parser.add_argument('--config', dest='config_path', default='config.example.yaml')

    args = parser.parse_args()
    config = register_app_config(args.config_path)
    setup_logging(config)

    app = build_app()
    setup_logging(app, config)
