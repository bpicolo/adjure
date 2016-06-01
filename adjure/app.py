# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys

import staticconf
from flask import Flask
from logstash_formatter import LogstashFormatterV1

from adjure.models.base import bind_database_engine
from adjure.routes.auth import auth_page


DB_HOST_ENV_VAR = 'ADJURE_DB_HOST'


def register_app_config(config_path):
    staticconf.YamlConfiguration(config_path, namespace='adjure')
    return staticconf.NamespaceReaders('adjure')


def setup_logging(app, config):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LogstashFormatterV1())
    app.logger.addHandler(handler)


def build_app():
    app = Flask(__name__)
    app.register_blueprint(auth_page)
    return app


parser = argparse.ArgumentParser(description='Run the adjure server')
parser.add_argument('--config', dest='config_path', default='config.example.yaml')

args = parser.parse_args()
config = register_app_config(args.config_path)

if not os.environ.get(DB_HOST_ENV_VAR, None):
    raise ValueError(
        '{} is required for Adjure to connect to a database.'.format(DB_HOST_ENV_VAR)
    )

bind_database_engine(os.environ[DB_HOST_ENV_VAR])
application = build_app()
setup_logging(application, config)
