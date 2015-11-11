# -*- coding: utf-8 -*-
import pytest

import staticconf.testing


@pytest.yield_fixture(scope='session', autouse=True)
def mock_configuration():
    with staticconf.testing.MockConfiguration(
        {
            'key_valid_duration': 30,
            'database': {
                'connection_string': ''
            }
        },
        namespace='adjure',
    ):
        yield
