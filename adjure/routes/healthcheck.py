# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import jsonify

from adjure.lib.auth import load_user


healthcheck_page = Blueprint('healthcheck', __name__)


@healthcheck_page.route('/healthcheck', methods=['GET'])
def healthcheck():
    # Make sure the DB connection is dandy
    load_user(1)
    return jsonify({})
