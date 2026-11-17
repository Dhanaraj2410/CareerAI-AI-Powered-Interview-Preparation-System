import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Resume


class ResumeApiOwnershipTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='SafePassword123!')
        self.other = User.objects.create_user(username='other', password='SafePassword123!')
        self.resume = Resume.objects.create(user=self.owner, title='Owner CV', skills='Python')

    def test_anonymous_clients_cannot_list_resumes(self):
        response = self.client.get(reverse('api_resume_list'))
        self.assertEqual(response.status_code, 401)

    def test_user_cannot_read_another_users_resume(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('api_resume_detail', args=[self.resume.id]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_create_resume(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('api_resume_list'),
            data=json.dumps({'title': 'New CV', 'skills': ['Python', 'Django']}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Resume.objects.filter(user=self.owner, title='New CV').exists())
