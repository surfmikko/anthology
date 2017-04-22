"""Common configuration for tests"""

import pytest

from anthology.api import get_app


@pytest.fixture(scope="function")
def client_fx():
    """Return test client for the application"""
    app = get_app()
    return app.test_client()
