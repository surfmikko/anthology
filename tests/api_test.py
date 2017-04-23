"""Test the `anthology/api` module"""

from json import loads

import pytest

from anthology.aggregate import calculate_totals


@pytest.mark.parametrize('uri', [
    '/songs', '/songs/avg', '/songs/search'])
def test_response_200(client_fx, uri):
    """All given `uri` should return valid HTTP 200 OK response.

    Additionally response headers and input format should be valid json.

    """
    response = client_fx.get(uri)

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert isinstance(loads(response.data), dict)


@pytest.mark.parametrize("uri", [
    '/', '/songs/rating', '/sogs'])
def test_404(client_fx, uri):
    """Test that API return correct HTTP 404 responses"""
    response = client_fx.get(uri)
    assert response.status_code == 404
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


def test_search(response_fx):
    """GET /songs/search?message="""

    response = response_fx('/songs/search?message=fastfinger')
    assert len(response["data"]) == 1
    assert response["data"][0]["title"] == 'Awaki-Waki'

    response = response_fx('/songs/search?message=waki')
    assert len(response["data"]) == 1
    assert response["data"][0]["artist"] == 'Mr Fastfinger'


def test_search_iteration(response_fx):
    """GET /songs/search?message=&limit=

    Test iteration over search results.

    """

    response = response_fx('/songs/search?message=ing')
    assert len(response["data"]) == 4
    assert response["data"][0]["artist"] == 'Mr Fastfinger'

    response = response_fx('/songs/search?message=ing&limit=3')
    assert len(response["data"]) == 3

    assert 'message' in response["next"]
    assert 'limit' in response["next"]
    assert 'previous_id' in response["next"]

    response = response_fx(response["next"])
    assert len(response["data"]) == 1


def test_search_word(response_fx):
    """GET /songs/search?word=

    Word search searches only full word. Partial matches should not return any
    result.

    """

    response = response_fx('/songs/search?word=the')
    assert len(response["data"]) == 10

    response = response_fx('/songs/search?word=ing')
    assert response["data"] == []


def test_rating(response_fx, client_fx):
    """GET /songs/rating/<id>
    POST /songs/rating/<id>

    Test good rating values.

    """
    response = response_fx('/songs')
    song = response["data"][0]
    assert song["rating"] == 5

    rating = response_fx(song["rating_url"])
    assert rating["rating"] == 5

    response = client_fx.post(song["rating_url"], data={'rating': 1})
    rating = loads(response.data)
    assert rating["rating"] == 1

    rating = response_fx(song["rating_url"])
    assert rating["rating"] == 1


def test_rating_invalid(response_fx, client_fx):
    """POST /songs/rating/<id>

    Test invalid rating values.

    """
    response = response_fx('/songs')
    song = response["data"][0]
    assert song["rating"] == 5

    response = client_fx.post(song["rating_url"], data={'rating': 0})
    message = loads(response.data)
    assert response.status_code == 400
    assert '1 and 5' in message["message"]["rating"]

    rating = response_fx(song["rating_url"])
    assert rating["rating"] == 5
