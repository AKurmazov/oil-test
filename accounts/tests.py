from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from knox.models import AuthToken


class RegistrationTestCase(APITestCase):

    credentials = {
            'username': 'test',
            'password': 'test'
        }

    def test_registration(self):
        response = self.client.post(reverse('register'), data=self.credentials)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginTestCase(APITestCase):

    login_url = reverse('login')
    credentials = {
        'username': 'test',
        'password': 'test'
    }

    def setUp(self):
        self.user = User.objects.create_user(**self.credentials)

    def test_login_success(self):
        response = self.client.post(self.login_url, data=self.credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'test')

    def test_login_fail(self):
        wrong_credentials = {
            'username': 'incorrect',
            'password': 'incorrect'
        }
        response = self.client.post(self.login_url, data=wrong_credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTestCase(APITestCase):

    logout_url = reverse('logout')

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.token = AuthToken.objects.create(user=self.user)[1]
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_user_authenticated_and_logout(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_unauthenticated_and_failed_logout(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
