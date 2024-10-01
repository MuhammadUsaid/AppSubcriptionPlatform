from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import App, Plan, Subscription

class LoginAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser2', password='testpassword')
        self.login_url = '/login'
        self.signup_url = '/signup'
        self.logout_url = '/logout'
        self.token = None

    def test_successful_login(self):
        data = {
            'username': 'testuser2',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        # Save the token for later use
        self.token = response.data['token']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

    def test_login_with_incorrect_password(self):
        data = {
            'username': 'testuser2',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_with_non_existent_user(self):
        data = {
            'username': 'nonexistentuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_with_missing_username(self):
        data = {
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_missing_password(self):
        data = {
            'username': 'testuser2'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_creation_on_login(self):
        data = {
            'username': 'testuser2',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_successful_signup(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_with_existing_username(self):
        data = {
            'username': 'testuser2',
            'password': 'newpassword',
            'email': 'newuser@example.com'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('username', response.data)

    def test_signup_with_invalid_email(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'invalidemail'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)

    def test_signup_with_missing_fields(self):
        data = {
            'username': 'newuser'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('password', response.data)
        # self.assertIn('email', response.data)

    def test_successful_logout(self):
        # First, we need to log in to get a valid token
        login_data = {
            'username': 'testuser2',
            'password': 'testpassword'
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.token = login_response.data['token']
        self.assertIsNotNone(self.token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_without_token(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AppAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.app_url = '/app/'
        self.app_detail_url = '/app/{}/'
        self.subscription_url = '/app/sub/{}/'
        
        # Create a test app
        self.app = App.objects.create(user=self.user, name='Test App')
        
        # Create test plans
        self.free_plan = Plan.objects.create(name='FREE')
        self.pro_plan = Plan.objects.create(name='PRO')

    def test_app_list(self):
        response = self.client.get(self.app_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test App')

    def test_app_create(self):
        data = {'name': 'New App', 'description': 'meaow'}
        response = self.client.post(self.app_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(App.objects.count(), 2)
        self.assertEqual(App.objects.last().name, 'New App')

    def test_app_create_without_name(self):
        data = {}
        response = self.client.post(self.app_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_app_detail(self):
        response = self.client.get(self.app_detail_url.format(self.app.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test App')

    def test_app_detail_not_found(self):
        response = self.client.get(self.app_detail_url.format(999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_app_update(self):
        data = {'name': 'Updated App'}
        response = self.client.put(self.app_detail_url.format(self.app.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.app.refresh_from_db()
        self.assertEqual(self.app.name, 'Updated App')

    def test_app_delete(self):
        response = self.client.delete(self.app_detail_url.format(self.app.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(App.objects.count(), 0)

    def test_subscription_update(self):
        # Ensure the app has a subscription with the FREE plan
        Subscription.objects.create(app=self.app, plan=self.free_plan)
        self.app.refresh_from_db()
        
        # Verify initial subscription
        self.assertEqual(self.app.subscription.plan, self.free_plan)
        data = {'plan': 'PRO'}
        response = self.client.put(self.subscription_url.format(self.app.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.app.refresh_from_db()
        self.assertEqual(self.app.subscription.plan.name, 'PRO')

    def test_subscription_update_invalid_plan(self):
        data = {'plan': 'INVALID'}
        response = self.client.put(self.subscription_url.format(self.app.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_update_app_not_found(self):
        data = {'plan': 'PRO'}
        response = self.client.put(self.subscription_url.format(999), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_access(self):
        self.client.credentials()  # Remove token authentication
        response = self.client.get(self.app_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_user_app(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        other_app = App.objects.create(user=other_user, name='Other App')
        response = self.client.get(self.app_detail_url.format(other_app.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
