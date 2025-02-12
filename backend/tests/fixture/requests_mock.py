# Python imports
import json
import re

# Pip imports
from fastapi import status

# Internal imports
from src.config import settings
from tests.fixture import Auth0MockData
from tests.fixture.auth0_management import mock_user_data


AUTH0_MOCK = Auth0MockData()


def mocked_requests_auth(method, url, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        @property
        def ok(self):
            if self.status_code < status.HTTP_400_BAD_REQUEST:
                return True
            return False

    data = json.loads(kwargs.get('data', '{}'))
    if re.match(fr"{settings.BASE_AUTH_URL}/users/(auth0\|)?([\d\w]+-?)+/roles", url):
        if method == "GET":
            return MockResponse(AUTH0_MOCK.AUTH0_USER_ROLE(), status.HTTP_200_OK)

        if method == "POST":
            return MockResponse({}, status.HTTP_200_OK)

        if method == "DELETE":
            return MockResponse({}, status.HTTP_204_NO_CONTENT)

    if re.match(fr"{settings.BASE_AUTH_URL}/users/auth0\|([\d\w]+-?)+", url) and method == "PATCH":
        return MockResponse(AUTH0_MOCK.AUTH0_UPDATE_USER(data=data, user_id=url.split("|")[1]), status.HTTP_200_OK)

    if re.match(fr"{settings.BASE_AUTH_URL}/users", url):
        if method == "GET":
            return MockResponse(AUTH0_MOCK.AUTH0_LIST_USERS(data=mock_user_data()), status.HTTP_200_OK)

        if method == "POST":
            return MockResponse(AUTH0_MOCK.AUTH0_CREATE_USER(data=data), status.HTTP_201_CREATED)

        if method == "DELETE":
            return MockResponse({}, status.HTTP_204_NO_CONTENT)

    if re.match(fr"{settings.BASE_AUTH_URL}/tickets", url) and method == "POST":
        return MockResponse(AUTH0_MOCK.AUTH0_CREATE_PASSWORD_CHANGE_TICKET(data=data), status.HTTP_200_OK)

    if re.match(fr"{settings.BASE_AUTH_URL}/roles/([\d\w]+-?)+/permissions", url):
        if method == "GET":
            return MockResponse(AUTH0_MOCK.AUTH0_ROLES_PERMISSIONS(), status.HTTP_200_OK)

        if method == "POST":
            return MockResponse(AUTH0_MOCK.AUTH0_PERMISSIONS(), status.HTTP_200_OK)

        if method == "DELETE":
            return MockResponse({}, status.HTTP_204_NO_CONTENT)

    if url == f"{settings.BASE_AUTH_URL}/roles/12f29f09-0091-4aa5-9351-b61171557a7d/users" and method == "POST":
        return MockResponse({}, status.HTTP_200_OK)

    if re.match(fr"{settings.BASE_AUTH_URL}/roles", url):
        if method == "GET":
            return MockResponse(AUTH0_MOCK.AUTH0_USER_ROLE(), status.HTTP_200_OK)

        if method == "POST":
            return MockResponse(AUTH0_MOCK.AUTH0_CREATE_ROLE(data), status.HTTP_200_OK)

    if re.match(fr"{settings.BASE_AUTH_URL}/resource-servers/{settings.AUTH0_RESOURCE_SERVER}", url):
        if method == "GET":
            return MockResponse(AUTH0_MOCK.AUTH0_RESOURCE_SERVER_BY_ID(data=data), status.HTTP_200_OK)

        if method == "PATCH":
            return MockResponse({}, status.HTTP_200_OK)

    if re.match(fr"https://{settings.AUTH0_DOMAIN}/oauth/token", url):
        if method == "POST":
            return MockResponse(AUTH0_MOCK.AUTH0_TOKEN(), status.HTTP_200_OK)

    return MockResponse({}, status.HTTP_400_BAD_REQUEST)


def mocked_requests_get(url, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        @property
        def ok(self):
            if self.status_code < status.HTTP_400_BAD_REQUEST:
                return True
            return False

    if url == f'{settings.EMAIL_BASE_URI}/v4/address/validate':
        return MockResponse(
            {
                "address": "test@container-crm.com",
                "is_disposable_address": False,
                "is_role_address": False,
                "reason": [],
                "result": "deliverable",
                "risk": "low",
            },
            status.HTTP_200_OK,
        )

    return MockResponse(None, status.HTTP_404_NOT_FOUND)


def mocked_requests_post(url, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        @property
        def ok(self):
            if self.status_code < status.HTTP_400_BAD_REQUEST:
                return True
            return False

    if url == f'{settings.EMAIL_BASE_URI}/v3/mg.usacontainers.co/messages':
        return MockResponse({}, status.HTTP_200_OK)

    if re.match(settings.BASE_AUTH_URL, url):
        return MockResponse({}, status.HTTP_200_OK)

    return MockResponse(None, status.HTTP_404_NOT_FOUND)
