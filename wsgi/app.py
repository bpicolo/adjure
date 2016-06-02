# -*- coding: utf-8 -*-
import argparse
import os

from adjure.app import build_app
from adjure.app import register_app_config
from adjure.app import setup_logging
from adjure.models.base import bind_database_engine

DB_HOST_ENV_VAR = 'ADJURE_DB_HOST'


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
