import json
from unittest.mock import Mock
from urllib import parse

import pytest
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate
from django.test import override_settings
from django.urls import reverse

from authentication.factories import UserFactory, StaffUserFactory
from authentication.models import User
from authentication.serializers import UserSerializer
from authentication.views import CreateUserView
from shared import frontend_urls
from .utils import assert_unauthenticated

pytestmark = [pytest.mark.django_db]

USER_EMAIL = "user@test.com"
VALID_PASSWORD = "test_password123"
INVALID_PASSWORD = "wrong_password123"
TEST_TOKEN = "test_token"

USER_DATA = {
    "email": USER_EMAIL,
    "password": VALID_PASSWORD,
}

GOOGLE_USER_DATA = {
    "email": USER_EMAIL,
    "token": TEST_TOKEN,
    "provider": User.PROVIDER_GOOGLE,
}

FACEBOOK_USER_DATA = {
    **GOOGLE_USER_DATA,
    "provider": User.PROVIDER_FACEBOOK,
}

SUCCESSFUL_FACEBOOK_RESPONSE = Mock(
    json=lambda: {"access_token": "test_access_token", "email": USER_EMAIL}, ok=True
)
FAILED_FACEBOOK_RESPONSE = Mock(json=lambda: {"error": "bad_token"}, ok=False)


class TestLogin:
    def test_login(self, authenticate_and_test):
        UserFactory(**USER_DATA)
        authenticate_and_test("authentication:login", USER_DATA)

    def test_login_wrong_password(self, authenticate_and_test):
        UserFactory(**USER_DATA)
        data = {
            **USER_DATA,
            "password": INVALID_PASSWORD,
        }
        authenticate_and_test("authentication:login", data, success=False)


class TestRegister:
    @pytest.mark.parametrize(
        "password",
        [
            "test_password",  # No number
            "837493938481",  # No letter
            "password1",  # Too common
            "uam38m",  # Too short
        ],
    )
    def test_register_with_bad_password(self, authenticate_and_test, password):
        data = {
            **USER_DATA,
            "password": password,
        }
        authenticate_and_test("authentication:register", data, success=False)

    def test_register_with_bad_email(self, authenticate_and_test):
        data = {
            **USER_DATA,
            "email": "abc@abc",
        }
        authenticate_and_test("authentication:register", data, success=False)

    def test_register_existing_email(self, authenticate_and_test):
        UserFactory(**USER_DATA)
        data = {**USER_DATA, "password": INVALID_PASSWORD}
        authenticate_and_test("authentication:register", data, success=False)

    def test_redirect(self, authenticate_and_test):
        redirect_url = "http://localhost:1234/test_path"
        data = {
            **USER_DATA,
            "next": redirect_url,
        }
        authenticate_and_test("authentication:register", data, redirect_url=redirect_url)

    @override_settings(VALID_REDIRECT_HOSTNAMES=["*.testing.com"])
    def test_redirect_wildcard(self, authenticate_and_test):
        redirect_url = "http://sub.testing.com"
        data = {
            **USER_DATA,
            "next": redirect_url,
        }
        authenticate_and_test("authentication:register", data, redirect_url=redirect_url)

    def test_ignores_bad_redirect_param(self, authenticate_and_test):
        data = {
            **USER_DATA,
            "next": "https://badsite.com",
        }
        authenticate_and_test("authentication:register", data)


class TestLogout:
    def test_logout(self, client, authenticate_and_test):
        authenticate_and_test("authentication:register", USER_DATA)
        response = client.get(reverse("logout"))

        assert response.status_code == 302
        assert response.url == frontend_urls.LOGIN
        assert_unauthenticated(client)

    def test_logout_preserves_query_params(self, client, authenticate_and_test):
        authenticate_and_test("authentication:register", USER_DATA)
        query_params = {"test": "value"}
        response = client.get(reverse("logout"), query_params)

        assert response.status_code == 302

        parsed_url = parse.urlparse(response.url)
        assert parsed_url.path == frontend_urls.LOGIN

        query_string = parse.urlencode(query_params)
        assert parsed_url.query == query_string

        assert_unauthenticated(client)

    @override_settings(VALID_REDIRECT_HOSTNAMES=["*.testing.com"])
    def test_logout_redirects_to_logout_redirect(self, client, authenticate_and_test):
        authenticate_and_test("authentication:register", USER_DATA)
        test_url = "https://www.testing.com"
        params = {"logoutNext": test_url}
        response = client.get(reverse("logout"), params)

        assert response.status_code == 302
        assert response.url == test_url
        assert_unauthenticated(client)

    @override_settings(VALID_REDIRECT_HOSTNAMES=["*.testing.com"])
    def test_logout_does_not_redirect_to_bad_domain(self, client, authenticate_and_test):
        authenticate_and_test("authentication:register", USER_DATA)
        params = {"logoutNext": "https://www.badsite.com"}
        response = client.get(reverse("logout"), params)

        assert response.status_code == 302
        parsed_url = parse.urlparse(response.url)
        assert parsed_url.path == frontend_urls.LOGIN
        assert_unauthenticated(client)


class TestCreateUserView(APITestCase):
    def test_create_with_no_existing_user(self):
        staff_user = StaffUserFactory(**USER_DATA)

        factory = APIRequestFactory()
        view = CreateUserView.as_view()
        new_email = "newuser@test.com"
        request = factory.post(
            reverse("authentication:create_user"),
            {
                "email": new_email,
                "password": VALID_PASSWORD,
            },
            format="json",
        )
        force_authenticate(request, user=staff_user)
        response = view(request)
        new_user = User.objects.get(email=new_email)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)["portunus_uuid"], str(new_user.portunus_uuid)
        )

    def test_create_with_existing_user(self):
        staff_user = StaffUserFactory(**USER_DATA)

        factory = APIRequestFactory()
        view = CreateUserView.as_view()
        request = factory.post(reverse("authentication:create_user"), USER_DATA, format="json")
        force_authenticate(request, user=staff_user)
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["portunus_uuid"], staff_user.portunus_uuid
        )
        self.assertEqual(json.loads(response.content)["user_exists"], True)


class TestRetrieveDeleteUserView(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    @property
    def endpoint_path(self):
        return reverse(
            "authentication:retrieve_or_delete_user", args=[self.user.portunus_uuid]
        )

    def check_get(self, status_code):
        response = self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, status_code)

        if status_code == 200:
            self.assertDictEqual(response.json(), UserSerializer(self.user).data)

    def check_delete(self, status_code=204):
        response = self.client.delete(self.endpoint_path)
        self.assertEqual(response.status_code, status_code)

        user = User.objects.filter(pk=self.user.pk).first()
        if status_code == 204:
            self.assertIsNone(user)
        else:
            self.assertIsNotNone(user)

    def check_user(self, user_requesting, status_code=None):
        if user_requesting:
            self.client.force_authenticate(user_requesting)

        self.check_get(status_code or 200)
        self.check_delete(status_code or 204)

    def test_same_user(self):
        self.check_user(self.user)

    def test_staff_user(self):
        staff_user = StaffUserFactory()
        self.check_user(staff_user)

    def test_wrong_user(self):
        other_user = UserFactory()
        self.check_user(other_user, status_code=403)

    def test_unauthenticated_user(self):
        self.check_user(None, status_code=401)
