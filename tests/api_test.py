"""Test the `anthology/api` module"""

from json import loads

import pytest


@pytest.mark.parametrize('uri', [
    '/songs'])
def test_response_200(client_fx, uri):
    """All given `uri` should return valid HTTP 200 OK response.

    Additionally response headers and input format should be valid json.

    """
    response = client_fx.get(uri)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert isinstance(loads(response.data), dict)


def test_songs(response_fx):
    """Detailed tests for /songs resource"""

    response = response_fx('/songs')

    assert 'data' in response
    assert len(response["data"]) == 10
