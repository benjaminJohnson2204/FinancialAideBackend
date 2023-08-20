from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from users.models import User


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1',
            email='user1@gmail.com',
            password='password1'
        )
        cls.user2 = User.objects.create_user(
            username='user2',
            email='user2@gmail.com',
            password='password2'
        )

    def test_register_missing_fields(self):
        response = self.client.post(
            reverse('register'),
            {},
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(
            reverse('register'),
            {
                'username': 'test',
                'email': 'missingfields@gmail.com',
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_taken_username(self):
        response = self.client.post(
            reverse('register'),
            {
                'email': 'newuser@gmail.com',
                'username': 'user1',
                'password': 'newpassword',
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_valid(self):
        response = self.client.post(
            reverse('register'),
            {
                'email': 'newuser@gmail.com',
                'username': 'newuser',
                'password': 'newpassword',
            },
            'application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['username'], 'newuser')
        self.assertEqual(response.json()['email'], 'newuser@gmail.com')
        self.assertEqual(User.objects.filter(
            username='newuser',
            email='newuser@gmail.com',
        ).count(), 1)

    def test_login_missing_fields(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'user1',
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_incorrect_password(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'user1',
                'password': 'incorrect',
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_valid(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'user1',
                'password': 'password1',
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['email'], 'user1@gmail.com')
        self.assertEqual(response.json()['username'], 'user1')

    def test_whoami_unauthorized(self):
        response = self.client.get(
            reverse('whoami')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_whoami_valid(self):
        self.client.login(username='user2', password='password2')
        response = self.client.get(
            reverse('whoami')
        )
        self.assertEqual(response.json()['email'], 'user2@gmail.com')
        self.assertEqual(response.json()['username'], 'user2')

    def test_logout(self):
        self.client.login(username='user2', password='password2')
        response = self.client.post(
            reverse('logout')
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the client is no longer logged in
        response = self.client.get(
            reverse('whoami')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
