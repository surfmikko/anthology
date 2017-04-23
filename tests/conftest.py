"""Common configuration for tests"""

import logging

from json import loads

import pytest


from anthology.database import db_songs, db_averages
from anthology.dbimport import import_json
from anthology.api import get_app

logging.basicConfig(loglevel=logging.debug)

TEST_DB_PORT = 45684


def pytest_addoption(parser):
    """Configure test options"""

    parser.addoption(
        "--skip-text-index", action="store_true",
        help="Do not test MongoDB text indexes", default=False)


def pytest_runtest_setup(item):
    """This function is used by py.test, here for skipping unsafe test cases"""

    if 'text_index' in item.keywords:
        if item.config.getoption("--skip-text-index"):
            pytest.skip("Skipping tests requiring MongoDB text indexes")


@pytest.fixture(scope="function")
def client_fx():
    """Return test client for the application"""
    return get_app().test_client()


@pytest.fixture(scope="function")
def response_fx():
    """Return test client for the application"""

    client = get_app().test_client()

    def _get(uri):
        """Return server response as JSON"""
        response = client.get(uri)
        return loads(response.data)

    return _get


@pytest.mark.usefixtures('mongo_proc')
@pytest.fixture(autouse=True, scope='function')
def testdata_fx(request):
    """Use temporary MongoDB instance for testing"""

    db_songs().remove()
    db_averages().remove()
    import_json(
        'tests/data/songs.json',
        not request.config.getoption('--skip-text-index'))
