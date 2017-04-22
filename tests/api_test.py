"""Test the `anthology/api` module"""

from json import loads

import pytest


@pytest.mark.parametrize(['uri', 'response_data'], [
    ('/songs', [{'_id': 1}, {'_id': 2}])
    ])
def test_api_response_200(client_fx, uri, response_data):
    """Test resources with response 200"""
    response = client_fx.get(uri)
    assert response.status_code == 200
    assert loads(response.data) == response_data
