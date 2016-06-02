# -*- coding: utf-8 -*-
import logging
import sys

import staticconf
from flask import Flask
from logstash_formatter import LogstashFormatterV1

from adjure.routes.auth import auth_page
from adjure.routes.healthcheck import healthcheck_page


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
    app.register_blueprint(healthcheck_page)
    return app
