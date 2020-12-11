import pytest


def test_health_check(client):
    url = "/api/health-check"
    #response = app.test_client().get(url)
    response = client.get(url)
    assert response.status_code == 200


def test_recommend_and_return(client, backend_auth):
    
    # create a unique username
    # make the signup api call
    # make the oauth2 api call to obtain the token
    # use the token as header to authenticate request.

    url = "/api/ml/v1/recommendation"
    # null querystring should lead to 400.
    response = client.get(url, headers=backend_auth.create_headers())
    assert response.status_code == 400