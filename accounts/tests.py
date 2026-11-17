from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class RegistrationTests(TestCase):
    def test_register_creates_profile_and_logs_user_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'candidate',
            'first_name': 'Test',
            'last_name': 'Candidate',
            'email': 'candidate@example.com',
            'password': 'SafePassword123!',
            'confirm_password': 'SafePassword123!',
            'target_role': 'Python Developer',
        })

        self.assertRedirects(response, reverse('dashboard'))
        user = User.objects.get(username='candidate')
        self.assertTrue(user.check_password('SafePassword123!'))
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'candidate',
            'email': 'candidate@example.com',
            'password': 'SafePassword123!',
            'confirm_password': 'DifferentPassword123!',
            'target_role': 'Python Developer',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='candidate').exists())

    def test_api_registration_rejects_duplicate_email(self):
        User.objects.create_user(username='existing', email='candidate@example.com', password='SafePassword123!')
        response = self.client.post(
            reverse('api_register'),
            data='{"email":"candidate@example.com","password":"SafePassword123!"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 409)
