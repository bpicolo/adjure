# -*- coding: utf-8 -*-
from io import BytesIO

import qrcode
from flask import Blueprint
from flask import jsonify
from flask import send_file
from flask import request

from adjure.lib import auth

auth_page = Blueprint('auth', __name__)


@auth_page.route('/user/provision', methods=['POST'])
def user_provision():
    data = request.get_json(force=True)

    try:
        user = auth.provision_user(**data)
    except auth.UserCreationException as e:
        return jsonify(success=False, message=e.args[0])
    except Exception as e:
        return jsonify(success=False, message="An error occurred")

    return jsonify(success=True, user_id=user.user_id)


@auth_page.route('/user/authenticate', methods=['POST'])
def user_authenticate():
    data = request.get_json(force=True)

    for field in ('user_id', 'value'):
        if field not in data:
            return jsonify(success=False, message='{} is required'.format(field))

    data['value'] = data['value'].encode('ASCII')

    try:
        auth.validate_user(**data)
    except auth.ValidationException as e:
        return jsonify(success=False, message=e.args[0])

    return jsonify(success=True)


@auth_page.route('/user/qrcode', methods=['GET'])
def user_qrcode():
    auth_uri = auth.user_auth_uri(
        username=request.args['username'],
        user_id=request.args['user_id'],
    )
    if not auth_uri:
        return 'User not found', 404

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(auth_uri)
    qr.make(fit=True)
    image = qr.make_image()
    data = BytesIO()
    image.save(data)

    data.seek(0)
    return send_file(data, mimetype='image/png')
