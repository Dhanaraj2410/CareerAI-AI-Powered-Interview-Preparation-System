from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import UserProfile
from aptitude.models import AptitudeResult
from .progress import progress_snapshot


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


class ProgressSnapshotTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='progress', password='SafePassword123!')

    def test_new_candidate_has_no_fabricated_scores(self):
        snapshot = progress_snapshot(self.user)

        self.assertIsNone(snapshot['overall'])
        self.assertEqual(snapshot['scores'], {
            'aptitude': None,
            'resume': None,
            'technical': None,
            'communication': None,
        })
        self.assertEqual(snapshot['next_action']['url_name'], 'aptitude_home')
        self.assertEqual(snapshot['streak'], 0)

    def test_activity_is_counted_by_calendar_day(self):
        result = AptitudeResult.objects.create(
            user=self.user, difficulty='easy', category='all', score=8,
            total_questions=10, percentage=80,
        )
        result.created_at = timezone.now() - timedelta(days=1)
        result.save(update_fields=['created_at'])

        snapshot = progress_snapshot(self.user)

        self.assertEqual(snapshot['scores']['aptitude'], 80.0)
        self.assertEqual(snapshot['active_days'], 1)
        self.assertEqual(sum(day['count'] for day in snapshot['activity']), 1)

    def test_progress_api_requires_login(self):
        response = self.client.get(reverse('api_dashboard_progress'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse('api_dashboard_progress'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('activity', response.json())

    def test_dashboard_renders_with_unmeasured_scores(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Not started')
        self.assertContains(response, 'Take an aptitude assessment')
