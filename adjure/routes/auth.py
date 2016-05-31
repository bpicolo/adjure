# -*- coding: utf-8 -*-
from io import BytesIO

import qrcode
from flask import Blueprint
from flask import jsonify
from flask import send_file
from flask import request
from flask import Response

from adjure.lib import auth

auth_page = Blueprint('auth', __name__)


@auth_page.route('/user/provision', methods=['POST'])
def user_provision():
    data = request.get_json(force=True)

    try:
        user = auth.provision_user(**data)
    except auth.UserCreationException as e:
        return jsonify(error_message=e.args[0], error_code='INVALID_PARAMS'), 400

    return jsonify(user_id=user.user_id)


@auth_page.route('/user/auth_code', methods=['GET'])
def user_auth_code():
    return jsonify({
        'code': auth.get_auth_code_for_user(request.args['user_id'])
    })


@auth_page.route('/user/authenticate', methods=['POST'])
def user_authenticate():
    data = request.get_json(force=True)

    for field in ('user_id', 'auth_code'):
        if field not in data:
            return jsonify(
                error_message='{} is required'.format(field),
                error_code='INVALID_PARAMS'
            ), 400

    try:
        auth.authorize_user(data['user_id'], data['auth_code'].encode('ASCII'))
    except auth.ValidationException as e:
        return jsonify(
            error_message=e.args[0],
            error_code='VALIDATION_FAILURE'
        ), 400

    return jsonify({}), 200


@auth_page.route('/user/qrcode', methods=['GET'])
def user_qrcode():
    auth_uri = auth.user_auth_uri(
        issuer=request.args['issuer'],
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
    return Response(data, mimetype='image/png')
