import pytest
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


@override_settings(DEBUG=False)
@pytest.mark.parametrize(
    "whitelisted_domain",
    [
        "https://app.willing.com",
        "https://members.legalplans.com",
    ],
)
def test_cors_allows_whitelisted_domains(client, whitelisted_domain):
    response = client.get(reverse("set_csrf_cookie"), HTTP_ORIGIN=whitelisted_domain)
    assert response.has_header("access-control-allow-origin")


@override_settings(DEBUG=False)
@pytest.mark.parametrize(
    "unknown_domain",
    [
        "http://app.willing.com",
        "https://notwilling.com",
    ],
)
def test_cors_blocks_unknown_domains(client, unknown_domain):
    response = client.get(reverse("set_csrf_cookie"), Origin=unknown_domain)
    assert not response.has_header("access-control-allow-origin")
