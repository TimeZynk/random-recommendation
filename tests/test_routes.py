import pytest
import sys
from os import path
sys.path.append(path.abspath(path.join(__file__, '../../src')))
from recommendation import create_app


@pytest.fixture
def app():
    """Create and configure an app instance for each test."""
    app = create_app()
    return app


def test_health_check(app):
    url = '/api/health-check'
    response = app.test_client().get(url)
    assert response.status_code == 200

def test_recommend_and_return():
    pass


