# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode

import pytest

from adjure.app import build_app
from adjure.lib import auth


@pytest.yield_fixture
def adjure():
    with build_app().test_client() as adjure_:
        yield adjure_


def post(adjure, route, data):
    # Not a super convenient API, so wrap it
    resp = adjure.post(
        route,
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )
    resp.json = json.loads(resp.data.decode(resp.charset))
    return resp


def get(adjure, route, data):
    # Not a super convenient API, so wrap it
    resp = adjure.get('{}?{}'.format(route, urlencode(data)))
    resp.json = json.loads(resp.data.decode(resp.charset))
    return resp


def test_user_provision(adjure):
    resp = post(adjure, '/user/provision', {'user_id': '1'})

    assert resp.status_code == 200
    assert resp.json['user_id'] == '1'
    assert len(resp.json['recovery_codes']) == auth.RECOVERY_CODE_COUNT


@pytest.mark.parametrize(
    'input_data',
    [
        ({},),
        ({'user_id': 2},),
    ]
)
def test_user_provision_bad_user_data(adjure, input_data):
    resp = post(adjure, '/user/provision', input_data)
    assert resp.status_code == 400


def test_provision_user_twice_fails(adjure):
    post(adjure, '/user/provision', {'user_id': '2'})
    resp = post(adjure, '/user/provision', {'user_id': '2'})

    assert resp.status_code == 400


def test_authenticate_user(adjure):
    user_id = '3'
    post(adjure, '/user/provision', {'user_id': user_id})

    auth_code_response = get(adjure, '/user/auth_code', {'user_id': user_id})
    authenticate_response = post(
        adjure,
        '/user/authenticate',
        {'user_id': user_id, 'auth_code': auth_code_response.json['code']}
    )

    assert authenticate_response.status_code == 200


def test_authenticate_user_failure(adjure):
    user_id = '3'
    post(adjure, '/user/provision', {'user_id': user_id})

    authenticate_response = post(
        adjure,
        '/user/authenticate',
        {'user_id': user_id, 'auth_code': '99999'}
    )
    assert authenticate_response.status_code == 400


def test_validate_recovery_code(adjure):
    user_id = '4'
    resp = post(adjure, '/user/provision', {'user_id': user_id})

    recovery_code = resp.json['recovery_codes'][0]

    recovery_authenticate_response = post(
        adjure,
        '/user/recovery/authenticate',
        {'user_id': user_id, 'recovery_code': recovery_code}
    )
    assert recovery_authenticate_response.status_code == 200


def test_failed_validate_recovery_code(adjure):
    user_id = '5'
    post(adjure, '/user/provision', {'user_id': user_id})

    recovery_authenticate_response = post(
        adjure,
        '/user/recovery/authenticate',
        {'user_id': user_id, 'recovery_code': 'lolthisisntarealcode'}
    )
    assert recovery_authenticate_response.status_code == 400


def test_regenerate_recovery_codes(adjure):
    user_id = '6'
    resp = post(adjure, '/user/provision', {'user_id': user_id})
    recovery_codes = set(resp.json['recovery_codes'])

    regenerated_code_response = post(
        adjure,
        '/user/recovery/regenerate',
        {'user_id': user_id}
    )
    regenerated_codes = set(regenerated_code_response.json['recovery_codes'])

    assert recovery_codes != regenerated_codes
    assert len(recovery_codes) == 10
    assert len(regenerated_codes) == 10
