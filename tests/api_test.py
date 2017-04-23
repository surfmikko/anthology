"""Test the `anthology/api` module"""

from json import loads

import pytest

from anthology.aggregate import calculate_totals


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
    """Test the /songs list"""

    response = response_fx('/songs')

    assert 'data' in response
    assert len(response["data"]) == 10


def test_songs_iteration(response_fx):
    """Test iteration of /songs list"""

    response = response_fx('/songs?limit=2')
    songs = response["data"]
    assert len(response["data"]) == 2

    assert '&' in response["next"]
    assert '?' in response["next"]

    for _ in range(10):
        response = response_fx(response["next"])
        songs = songs + response["data"]
        if response["next"] is None:
            break

    assert len(songs) == 11


def test_average_difficulty(response_fx):
    """Test average level for songs"""

    response = response_fx('/songs/avg')
    assert "average_difficulty" in response
    assert response["average_difficulty"] == 10.32
    assert response["algorithm"] == 'trivial'

    response = response_fx('/songs/avg?level=9')
    assert response["average_difficulty"] == 9.69

    calculate_totals()

    response = response_fx('/songs/avg?level=9&algorithm=fun')
    assert response["average_difficulty"] == 9.69
    assert response["algorithm"] == 'fun'

    response = response_fx('/songs/avg?algorithm=fun')
    assert response["average_difficulty"] == 10.32
    assert response["algorithm"] == 'fun'
