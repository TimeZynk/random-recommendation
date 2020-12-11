from os import path
import sys
import requests
import json

sys.path.append(path.abspath(path.join(__file__, "../../src")))
from recommendation import create_app
import pytest
import os


@pytest.fixture
def app():
    """Create and configure an app instance for each test."""
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def backend_auth():
    return BackendAuthActions(
        backend_url="http://192.168.1.20:8989",
        name="name",
        username="username",
        email="email@email",
        company_name="companyname",
        password="password",
        grant_type="password",
        client_id="tzcontrol@v1.0.0"
    )


class BackendAuthActions(object):
    def __init__(
        self,
        backend_url,
        name,
        username,
        email,
        company_name,
        password,
        grant_type,
        client_id,
    ):
        self.backend_url = backend_url
        self.name = name
        self.username = username
        self.email = email
        self.company_name = company_name
        self.password = password
        self.grant_type = grant_type
        self.client_id = client_id
        self.headers = dict()

    def sign_up(self):
        payload = {
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "company-name": self.company_name,
            "password": self.password
        }
        headers = {"Content-Type": "application/json"}

        return requests.post(
            self.backend_url + "/api/signup/v1/token",
            data=json.dumps(payload),
            headers=headers
        )

    def fetch_token(self):
        payload = {
            "grant_type": self.grant_type,
            "username": self.username,
            "client_id": self.client_id,
            "password": self.password,
        }
        headers = {"Content-Type": "application/json"}
        return requests.post(
            self.backend_url + "/api/oauth2/v1/token",
            data=json.dumps(payload),
            headers=headers
        )

    def create_headers(self):
        # error handling needed?
        self.sign_up()
        token_text = self.fetch_token().text
        token_dict = json.loads(token_text)
        authorization = "Bearer " + token_dict['access_token']
        self.headers['Authorization'] = authorization
        return self.headers
