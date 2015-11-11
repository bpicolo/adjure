# -*- coding: utf-8 -*-
import math
import os
import time

import staticconf
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.twofactor import InvalidToken
from cryptography.hazmat.primitives.twofactor.totp import TOTP

from adjure.models.base import session
from adjure.models.auth_user import AuthUser


SECRET_KEY_BYTES = 20


class ValidationException(ValueError):
    """Raised for invalid auth attempt"""


class UserCreationException(ValueError):
    """Raised when invalid user is created"""


def load_user(user_id):
    return session.query(AuthUser).filter(AuthUser.user_id == user_id).first()


def provision_user(user_id, key_length=None):
    config = staticconf.NamespaceReaders('adjure')
    if key_length is None:
        key_length = config.read('auth.default_key_length')

    if not 6 == key_length:
        raise UserCreationException('{} is not a valid key_length. Must be 6 for now'.format(key_length))
    if load_user(user_id):
        raise UserCreationException('User id {} already provisioned.'.format(user_id))

    secret = os.urandom(SECRET_KEY_BYTES)
    auth_user = AuthUser(user_id=user_id, secret=secret, key_length=key_length)

    session.add(auth_user)
    session.commit()

    return auth_user


def validate_user(user_id, value):
    """
    user_id: int
    value: UTF8 encoded bytes
    """
    config = staticconf.NamespaceReaders('adjure')
    key_valid_duration = config.read_int('key_valid_duration', default=30)
    sliding_windows = config.read_int('sliding_windows', default=1)
    user = load_user(user_id)

    if not user:
        raise ValidationException('{} is not a known user.'.format(user_id))

    totp_verify(
        user.secret,
        user.key_length,
        value,
        math.floor(time.time()),
        key_valid_duration,
        sliding_windows,
    )


def get_totp(secret, key_length, key_valid_duration):
    return TOTP(
        secret,
        key_length,
        SHA1(),
        key_valid_duration,
        backend=default_backend(),
    )


def totp_verify(secret, key_length, value, current_time, key_valid_duration, sliding_windows):
    totp = get_totp(
        secret,
        key_length,
        key_valid_duration,
    )
    for window_time in sliding_time_window(
        current_time, key_valid_duration, sliding_windows,
    ):
        try:
            totp.verify(value, window_time)
        except InvalidToken:
            pass
        else:
            return True

    raise ValidationException('Value was invalid')


def sliding_time_window(current_time, key_valid_duration, sliding_windows):
    return range(
        current_time - (key_valid_duration * sliding_windows),
        current_time + (key_valid_duration * sliding_windows) + 1,
        key_valid_duration,
    )


def user_auth_uri(username, user_id):
    """
    :param username: The username that should show up on the user's auth app
    """
    issuer = 'blah'
    config = staticconf.NamespaceReaders('adjure')
    user = load_user(user_id)

    if not user:
        return None

    totp = get_totp(
        user.secret,
        user.key_length,
        config.read_int('key_valid_duration', default=30),
    )

    return totp.get_provisioning_uri(username, issuer)
