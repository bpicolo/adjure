# -*- coding: utf-8 -*-
import pytest
import staticconf
import staticconf.testing

from adjure.models import base


@pytest.yield_fixture(scope='session', autouse=True)
def mock_configuration():
    with staticconf.testing.MockConfiguration(
        {
            'auth': {
                'key_valid_duration': 30,
            },
        },
        namespace='adjure',
    ):
        engine = base.bind_database_engine('sqlite://')
        base.Base.metadata.create_all(engine)
        yield
