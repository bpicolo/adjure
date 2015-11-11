# -*- coding: utf-8 -*-
import os
import pytest

import staticconf.testing
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from cryptography.hazmat.primitives.hashes import SHA256

from adjure.lib import auth
from adjure.models.auth_user import AuthUser


@pytest.yield_fixture(scope='session', autouse=True)
def mock_configuration():
    with staticconf.testing.MockConfiguration(
        {
            'key_valid_duration': 30
        },
        namespace='adjure',
    ):
        yield


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
    totp = TOTP(
        secret,
        key_length,
        SHA256(),
        30,
        backend=default_backend(),
    )
    value = totp.generate(current_time)

    assert auth.totp_verify(secret, key_length, value, current_time, 30, 0)
    assert auth.totp_verify(secret, key_length, value, current_time, 30, 1)
    assert not auth.totp_verify(secret, key_length, value, current_time, 60, 0)

    assert not auth.totp_verify(secret, key_length, b'999999', current_time, 30, 0)


def test_totp_verify_60_window():
    secret = os.urandom(20)
    key_length = 6
    current_time = 400
    totp = TOTP(
        secret,
        key_length,
        SHA256(),
        60,
        backend=default_backend(),
    )
    value = totp.generate(current_time)
    previous_window = totp.generate(340)
    next_window = totp.generate(460)

    assert auth.totp_verify(secret, key_length, value, current_time, 60, 0)
    assert not auth.totp_verify(secret, key_length, previous_window, current_time, 60, 0)
    assert not auth.totp_verify(secret, key_length, next_window, current_time, 60, 0)

    assert auth.totp_verify(secret, key_length, value, current_time, 60, 1)
    assert auth.totp_verify(secret, key_length, previous_window, current_time, 60, 1)
    assert auth.totp_verify(secret, key_length, next_window, current_time, 60, 1)

    assert not auth.totp_verify(secret, key_length, b'999999', current_time, 60, 0)
    assert not auth.totp_verify(secret, key_length, value, current_time, 30, 0)

