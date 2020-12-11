import pytest


def test_backend_actions(backend_auth):
    assert backend_auth.sign_up().status_code == 200
    fetch_token = backend_auth.fetch_token() 
    assert fetch_token.status_code == 200
    headers = backend_auth.create_headers()
    assert 'Authorization' in headers.keys()
