# -*- coding: utf-8 -*-
from io import BytesIO

import qrcode
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response
from jsonschema import validate
from jsonschema import ValidationError

from adjure.lib import auth

auth_page = Blueprint('auth', __name__)


USER_PROVISION_SCHEMA = {
    'type': 'object',
    'properties': {
        'user_id': {
            'type': 'string',
        },
        'key_length': {
            'type': 'number',
            'enum': list(auth.SUPPORTED_KEY_LENGTHS),
            'default': 6,
        },
        'key_valid_duration': {
            'type': 'number',
            'description': 'The length of time each code is valid for, seconds',
            'default': 30,
        },
        'hash_algorithm': {
            'type': 'string',
            'enum': list(auth.TOTP_HASH_ALGORITHMS.keys()),
            'description': 'Hash algorithm to pass to TOTP authentication',
            'default': 'SHA256',
        },
    },
    'required': ['user_id'],
}


@auth_page.route('/user/provision', methods=['POST'])
def user_provision():
    data = request.get_json(force=True)
    try:
        validate(data, USER_PROVISION_SCHEMA)
    except ValidationError as e:
        return jsonify(error_message=str(e), error_code='INVALID_PARAMS'), 400

    user = auth.provision_user(**data)
    return jsonify(user_id=user.user_id)


USER_AUTH_CODE_SCHEMA = {
    'type': 'object',
    'properties': {
        'user_id': {
            'type': 'string'
        },
    },
    'required': ['user_id'],
}


@auth_page.route('/user/auth_code', methods=['GET'])
def user_auth_code():
    try:
        validate(request.args, USER_AUTH_CODE_SCHEMA)
    except ValidationError as e:
        return jsonify(error_message=str(e), error_code='INVALID_PARAMS'), 400

    user = auth.load_user(request.args['user_id'])
    if not user:
        return jsonify(
            error_message='User {} has not been provisioned'.format(request.args['user_id']),
            error_code='USER_NOT_FOUND'
        ), 400

    return jsonify({
        'code': auth.get_auth_code_for_user(user)
    })


USER_AUTHENTICATE_SCHEMA = {
    'type': 'object',
    'properties': {
        'user_id': {
            'type': 'string',
        },
        'auth_code': {
            'type': 'string',
            'description': 'The TOTP code from the user\'s 2FA app',
        },
    },
    'required': ['user_id', 'auth_code'],
}


@auth_page.route('/user/authenticate', methods=['POST'])
def user_authenticate():
    data = request.get_json(force=True)
    try:
        validate(data, USER_AUTHENTICATE_SCHEMA)
    except ValidationError as e:
        return jsonify(error_message=str(e), error_code='INVALID_PARAMS'), 400

    try:
        auth.authorize_user(data['user_id'], data['auth_code'].encode('ASCII'))
    except auth.ValidationException as e:
        return jsonify(
            error_message=e.args[0],
            error_code='VALIDATION_FAILURE'
        ), 400

    return jsonify({}), 200


USER_QRCODE_SCHEMA = {
    'type': 'object',
    'properties': {
        'user_id': {
            'type': 'string',
        },
        'issuer': {
            'type': 'string',
            'description': 'The issuer of this TOTP code. Typically, your company name',
        },
        'username': {
            'type': 'string',
            'description': 'The username to display in the user\'s auth app',
        },
    },
    'required': ['user_id', 'issuer', 'username'],
}


def qr_code_image_as_bytes(auth_uri):
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

    return data


@auth_page.route('/user/qrcode', methods=['GET'])
def user_qrcode():
    try:
        validate(request.args, USER_QRCODE_SCHEMA)
    except ValidationError as e:
        return jsonify(error_message=str(e), error_code='INVALID_PARAMS'), 400

    auth_uri = auth.user_auth_uri(
        issuer=request.args['issuer'],
        username=request.args['username'],
        user_id=request.args['user_id'],
    )
    if not auth_uri:
        return 'User not found', 404

    return Response(qr_code_image_as_bytes(auth_uri), mimetype='image/png')
