# -*- coding: utf-8 -*-
import os

import pytest

from adjure.lib import auth


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
