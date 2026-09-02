import os
import sys
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerai.settings')
import django
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from interview.models import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewQuestionBank
from aptitude.models import AptitudeResult, Question, AptitudeAnswer

def seed_user_data():
    """
    Creates and imports essential user accounts, superusers, user profiles,
    and initial user activity records into MySQL database.
    """
    users_data = [
        {
            "username": "admin",
            "email": "admin@careerai.com",
            "first_name": "System",
            "last_name": "Administrator",
            "is_staff": True,
            "is_superuser": True,
            "target_role": "Python Developer",
            "bio": "CareerAI Platform System Administrator",
            "experience_level": "Senior / Lead"
        },
        {
            "username": "dhanaraj",
            "email": "dhanaraj@careerai.com",
            "first_name": "Dhanaraj",
            "last_name": "User",
            "is_staff": False,
            "is_superuser": False,
            "target_role": "Python Developer",
            "bio": "Passionate Python & AI Developer working on Django interview prep.",
            "experience_level": "Intermediate (1-3 years)"
        },
        {
            "username": "candidate1",
            "email": "candidate1@careerai.com",
            "first_name": "Alex",
            "last_name": "Candidate",
            "is_staff": False,
            "is_superuser": False,
            "target_role": "Data Scientist",
            "bio": "Aspiring Data Scientist focusing on ML models and NLP.",
            "experience_level": "Fresher / Entry Level"
        },
        {
            "username": "demouser",
            "email": "demo@careerai.com",
            "first_name": "Demo",
            "last_name": "Tester",
            "is_staff": False,
            "is_superuser": False,
            "target_role": "Machine Learning Engineer",
            "bio": "Demo candidate profile for system verification.",
            "experience_level": "Senior / Lead"
        }
    ]

    default_password = "UserPass123!"

    print("--- Importing User Data into MySQL Database ---")
    for u_data in users_data:
        user, created = User.objects.get_or_create(
            username=u_data["username"],
            defaults={
                "email": u_data["email"],
                "first_name": u_data["first_name"],
                "last_name": u_data["last_name"],
                "is_staff": u_data["is_staff"],
                "is_superuser": u_data["is_superuser"]
            }
        )
        if created:
            user.set_password(default_password)
            user.save()
            print(f"[OK] Created User: {user.username} (Password: {default_password})")
        else:
            print(f"[INFO] User Already Exists: {user.username}")

        # Import/Update User Profile
        profile, p_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "target_role": u_data["target_role"],
                "bio": u_data["bio"],
                "experience_level": u_data["experience_level"]
            }
        )
        if not p_created:
            profile.target_role = u_data["target_role"]
            profile.bio = u_data["bio"]
            profile.experience_level = u_data["experience_level"]
            profile.save()

    # Import initial Aptitude test result for demo user
    demo_user = User.objects.get(username="dhanaraj")
    if not AptitudeResult.objects.filter(user=demo_user).exists():
        apt_result = AptitudeResult.objects.create(
            user=demo_user,
            difficulty="medium",
            category="all",
            score=8,
            total_questions=10,
            percentage=80.0
        )
        print(f"[OK] Created initial AptitudeResult record for {demo_user.username} (80%)")

    # Import initial Interview Session for demo user
    if not InterviewSession.objects.filter(user=demo_user).exists():
        session = InterviewSession.objects.create(
            user=demo_user,
            role="Python Developer",
            mode="text",
            difficulty="medium",
            total_questions=5,
            current_section=1,
            total_score=85.0,
            avg_confidence=88.0,
            status="Completed",
            completed=True
        )
        print(f"[OK] Created initial InterviewSession record for {demo_user.username} (85%)")

    print("--- User Data Import to MySQL Complete! ---")

if __name__ == '__main__':
    seed_user_data()
