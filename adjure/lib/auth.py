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


# Google authenticator and many similar apps REQUIRE SHA1 + 6 length keys
# It's easy for the service to support other things but apps don't. :(
SECRET_KEY_BYTES = 20
SUPPORTED_KEY_LENGTHS = (6, 8)


class ValidationException(ValueError):
    """Raised for invalid auth attempt"""


class UserCreationException(ValueError):
    """Raised when invalid user is created"""


def load_user(user_id):
    return session.query(AuthUser).filter(AuthUser.user_id == user_id).first()


def provision_user(user_id, key_length=None, key_valid_duration=None):
    """Provision a totp user for the given user_id
    :param user_id: int
    :param key_length: int in SUPPORTED_KEY_LENGTHS
    """
    config = staticconf.NamespaceReaders('adjure')
    if key_length is None:
        key_length = config.read('auth.key_length', default=6)
    if key_valid_duration is None:
        key_valid_duration = config.read('auth.key_valid_duration', default=30)

    if key_length not in SUPPORTED_KEY_LENGTHS:
        raise UserCreationException('{} is not a valid key_length. Must be one of {}'.format(
            key_length,
            SUPPORTED_KEY_LENGTHS
        ))
    if load_user(user_id):
        raise UserCreationException('User id {} already provisioned.'.format(user_id))

    auth_user = AuthUser(
        user_id=user_id,
        secret=os.urandom(SECRET_KEY_BYTES),
        key_length=key_length,
        key_valid_duration=key_valid_duration
    )

    session.add(auth_user)
    session.commit()

    return auth_user


def authorize_user(user_id, value):
    """Authorize the user given a code entry.
    :param user_id: int
    :param value: ASCII encoded bytes
    """
    config = staticconf.NamespaceReaders('adjure')
    sliding_windows = config.read_int('sliding_windows', default=1)
    user = load_user(user_id)

    if not user:
        raise ValidationException('{} is not a known user.'.format(user_id))

    return totp_verify(
        user.secret,
        user.key_length,
        value,
        math.floor(time.time()),
        user.key_valid_duration,
        sliding_windows,
    )


def get_totp(secret, key_length, key_valid_duration):
    """Get the cryptography TOTP handler
    :param secret: bytes
    :param key_length: int length of totp key
    :param key_valid_duration: int duration each key is valid for
    """
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

    raise ValidationException('Invalid code was given.')


def sliding_time_window(current_time, key_valid_duration, sliding_windows):
    return range(
        current_time - (key_valid_duration * sliding_windows),
        current_time + (key_valid_duration * sliding_windows) + 1,
        key_valid_duration,
    )


def user_auth_uri(user_id, username, issuer):
    """
    :param username: The username that should show up on the user's auth app
    """
    user = load_user(user_id)
    if not user:
        return None

    totp = get_totp(
        user.secret,
        user.key_length,
        user.key_valid_duration,
    )

    return totp.get_provisioning_uri(username, issuer)
