"""Common configuration for tests"""

from json import loads

import pytest

import mongomock

import anthology.database
from anthology.database import collection
from anthology.api import get_app


@pytest.fixture(autouse=True, scope='function')
def patch_database_fx(monkeypatch):
    """Use MongoMock for testing"""

    connection = mongomock.MongoClient()
    monkeypatch.setattr(
        anthology.database, 'connection', lambda: connection)

    with open('tests/data/songs.json') as infile:
        for song_json in infile.readlines():
            collection().insert(loads(song_json))


@pytest.fixture(scope="function")
def client_fx():
    """Return test client for the application"""
    app = get_app()
    return app.test_client()


@pytest.fixture(scope="function")
def response_fx(client_fx):
    """Return test client for the application"""

    client = client_fx

    def _get(uri):
        """Return server response as JSON"""
        response = client.get(uri)
        return loads(response.data)

    return _get
