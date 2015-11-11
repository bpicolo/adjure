# -*- coding: utf-8 -*-
from base64 import b32encode
import os
import time
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest

from adjure.lib import auth


def test_provision_user():
    user_id = 10
    auth.provision_user(user_id)

    auth_user = auth.load_user(user_id)
    assert auth_user.user_id == 10
    assert len(auth_user.secret) == auth.SECRET_KEY_BYTES
    assert auth_user.key_length == 6


def test_provision_user_alternate_key_length():
    user_id = 11
    auth.provision_user(user_id, key_length=8)

    auth_user = auth.load_user(user_id)
    assert auth_user.key_length == 8


def test_unsupported_key_length():
    with pytest.raises(auth.UserCreationException):
        auth.provision_user(1, key_length=10)


def test_user_exists():
    user_id = 12
    auth.provision_user(user_id)
    with pytest.raises(auth.UserCreationException):
        auth.provision_user(user_id)


def test_authorize_user():
    user_id = 13
    user = auth.provision_user(user_id)

    totp = auth.get_totp(user.secret, user.key_length, 30)
    value = totp.generate(time.time())

    assert auth.authorize_user(user_id, value)


def test_authorize_user_not_found():
    user_id = 14
    with pytest.raises(auth.ValidationException):
        auth.authorize_user(user_id, 'foo')


def test_sliding_window():
    current_time = 400

    assert list(auth.sliding_time_window(current_time, 30, 0)) == [400]
    assert list(auth.sliding_time_window(current_time, 30, 1)) == [370, 400, 430]
    assert list(auth.sliding_time_window(current_time, 30, 2)) == [340, 370, 400, 430, 460]
    assert list(auth.sliding_time_window(current_time, 60, 1)) == [340, 400, 460]


def test_totp_verify():
    secret = os.urandom(20)
    key_length = 6
    current_time = 400
    totp = auth.get_totp(secret, key_length, 30)
    value = totp.generate(current_time)

    assert auth.totp_verify(secret, key_length, value, current_time, 30, 0)
    assert auth.totp_verify(secret, key_length, value, current_time, 30, 1)
    with pytest.raises(auth.ValidationException):
        auth.totp_verify(secret, key_length, value, current_time, 60, 0)
    with pytest.raises(auth.ValidationException):
        auth.totp_verify(secret, key_length, b'999999', current_time, 30, 0)


def test_totp_verify_60_window():
    secret = os.urandom(20)
    key_length = 6
    current_time = 400
    totp = auth.get_totp(secret, key_length, 60)

    value = totp.generate(current_time)
    previous_window = totp.generate(340)
    next_window = totp.generate(460)

    assert auth.totp_verify(secret, key_length, value, current_time, 60, 0)
    with pytest.raises(auth.ValidationException):
        auth.totp_verify(secret, key_length, previous_window, current_time, 60, 0)
    with pytest.raises(auth.ValidationException):
        auth.totp_verify(secret, key_length, next_window, current_time, 60, 0)

    assert auth.totp_verify(secret, key_length, value, current_time, 60, 1)
    assert auth.totp_verify(secret, key_length, previous_window, current_time, 60, 1)
    assert auth.totp_verify(secret, key_length, next_window, current_time, 60, 1)

    with pytest.raises(auth.ValidationException):
        auth.totp_verify(secret, key_length, b'999999', current_time, 60, 0)
    with pytest.raises(auth.ValidationException):
        auth.totp_verify(secret, key_length, value, current_time, 30, 0)


def test_auth_uri():
    user_id = 15
    user = auth.provision_user(user_id)

    auth_uri = urlparse(
        auth.user_auth_uri(user_id, 'ausername@example.org', 'someissuer'),
    )

    assert auth_uri.scheme == 'otpauth'
    assert auth_uri.netloc == 'totp'
    assert auth_uri.path == '/someissuer:ausername%40example.org'

    query = parse_qs(auth_uri.query)
    assert query['algorithm'] == ['SHA1']
    assert query['period'] == [str(user.key_valid_duration)]
    assert query['issuer'] == ['someissuer']
    assert query['secret'] == [b32encode(user.secret).decode('ASCII')]
    assert query['digits'] == [str(user.key_length)]
