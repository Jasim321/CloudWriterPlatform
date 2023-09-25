import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bookwriter.models import Collaboration, Book, UserProfile


class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'role': 'author',
        }

    def test_user_registration(self):
        url = reverse('signup')
        response = self.client.post(url, self.user_data, format='json')
        data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['response']['username'], 'testuser')
        self.assertEqual(data['response']['email'], 'testuser@example.com')
        self.assertEqual(data['response']['role'], 'author')
        self.assertEqual(data.get('success'), 'User created successfully.')

    def test_user_login(self):
        signup_url = reverse('signup')
        response = self.client.post(signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        login_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        login_url = reverse('login')
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn('access_token', data['response'])
        self.assertIn('refresh_token', data['response'])
        self.assertEqual(data.get('detail'), 'Login successful.')

    def test_user_logout(self):
        signup_url = reverse('signup')
        response = self.client.post(signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        login_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        login_url = reverse('login')
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        logout_url = reverse('logout')
        response = self.client.post(logout_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data.get('detail'), 'Logout successful.')


class GrantCollaborationAccessViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='Jasim', password='password')
        self.user_profile = UserProfile.objects.create(user=self.user, role="Author")
        self.collaborator_user = User.objects.create_user(username='collaborator', password='password')
        self.book = Book.objects.create(title='Test Book', author=self.user)
        self.collaboration = Collaboration.objects.create(
            user=self.collaborator_user,
            book=self.book,
            role='Collaborator',
            can_edit=False
        )
        self.client.force_login(self.user)

    def get_access_token(self, username, password):
        url = reverse('login')
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token_data = json.loads(response.content)
        access_token = token_data['response']['access_token']
        return access_token

    def test_revoke_access(self):
        access_token = self.get_access_token('Jasim', 'password')
        authorization_header = f'Bearer {access_token}'
        headers = {'HTTP_AUTHORIZATION': authorization_header}
        url = reverse('revoke-collaboration-access')
        data = {'collaborator_id': self.collaboration.id}
        response = self.client.put(url, data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.collaboration.refresh_from_db()
        self.assertFalse(self.collaboration.can_edit)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('message'), "Access revoked successfully")

    def test_grant_access(self):
        access_token = self.get_access_token('Jasim', 'password')
        authorization_header = f'Bearer {access_token}'
        headers = {'HTTP_AUTHORIZATION': authorization_header}
        url = reverse('grant-collaboration-access')
        data = {'collaborator_id': self.collaboration.id}
        response = self.client.put(url, data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.collaboration.refresh_from_db()
        self.assertTrue(self.collaboration.can_edit)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('message'), "Access granted successfully")
