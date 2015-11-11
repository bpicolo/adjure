# -*- coding: utf-8 -*-
import pytest
import staticconf
import staticconf.testing

from adjure.models import base


@pytest.yield_fixture(scope='session', autouse=True)
def mock_configuration():
    with staticconf.testing.MockConfiguration(
        {
            'key_valid_duration': 30,
            'database': {
                'connection_string': 'sqlite://'
            }
        },
        namespace='adjure',
    ):
        engine = base.bind_database_engine(staticconf.NamespaceReaders('adjure'))
        base.Base.metadata.create_all(engine)
        yield
