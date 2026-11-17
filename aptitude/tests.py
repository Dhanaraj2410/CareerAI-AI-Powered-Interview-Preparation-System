from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import AptitudeResult, Question


class AptitudeSubmissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='candidate', password='SafePassword123!')
        self.client.force_login(self.user)
        self.question = Question.objects.create(
            question='What is 2 + 2?', option_a='3', option_b='4',
            option_c='5', option_d='6', correct_answer='B',
            difficulty='easy', category='quantitative', topic='Arithmetic',
        )

    def test_submission_records_score_and_answer(self):
        response = self.client.post(reverse('aptitude_submit'), {
            'difficulty': 'easy',
            'category': 'quantitative',
            'question_ids': [str(self.question.id)],
            f'question_{self.question.id}': 'B',
        })

        result = AptitudeResult.objects.get(user=self.user)
        self.assertRedirects(response, reverse('aptitude_result', args=[result.id]))
        self.assertEqual(result.score, 1)
        self.assertEqual(result.percentage, 100.0)
        self.assertTrue(result.answers.get().is_correct)
