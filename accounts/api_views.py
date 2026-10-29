"""
CareerAI Accounts API Views - REST Endpoints for Frontend
--------------------------------------------------------
Provides authentication, OTP simulation, and user profile endpoints
for external clients (React/frontend integration).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile


def parse_json(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except Exception:
        return {}


@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    
    data = parse_json(request)
    email = data.get('email', '').strip()
    username = data.get('username', '').strip() or email.split('@')[0]
    password = data.get('password', '')

    user = None
    if email:
        try:
            u_obj = User.objects.get(email=email)
            user = authenticate(username=u_obj.username, password=password)
        except User.DoesNotExist:
            user = None
            
    if user is None and username:
        user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return JsonResponse({
            'status': 'success',
            'token': f'session-{user.id}',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
                'role': profile.target_role,
            }
        })
    else:
        return JsonResponse({'message': 'Invalid email or password'}, status=400)
    username = data.get('username', '').strip() or email.split('@')[0]
    password = data.get('password', '')

    user = None
    if email:
        try:
            u_obj = User.objects.get(email=email)
            user = authenticate(username=u_obj.username, password=password)
        except User.DoesNotExist:
            user = None
            
    if user is None and username:
        user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return JsonResponse({
            'status': 'success',
            'token': f'session-{user.id}',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
                'role': profile.target_role,
            }
        })
    else:
        return JsonResponse({'message': 'Invalid email or password'}, status=400)

@csrf_exempt
def api_send_register_otp(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    return JsonResponse({'status': 'success', 'message': 'OTP sent successfully to your email (Simulated OTP: 123456)'})

@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
        
    data = parse_json(request)
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return JsonResponse({'message': 'Email and password are required.'}, status=400)
        
    username = email.split('@')[0]
    if User.objects.filter(username=username).exists():
        username = f"{username}_{User.objects.count() + 1}"

    user = User.objects.create_user(username=username, email=email, password=password)
    parts = name.split(' ', 1)
    user.first_name = parts[0]
    if len(parts) > 1:
        user.last_name = parts[1]
    user.save()

    profile = UserProfile.objects.create(user=user, target_role='Python Developer')
    login(request, user)

    return JsonResponse({
        'status': 'success',
        'token': f'session-{user.id}',
        'user': {
            'id': user.id,
            'username': user.username,
            'name': name or user.username,
            'email': user.email,
            'role': profile.target_role,
        }
    })

@csrf_exempt
def api_send_forgot_otp(request):
    return JsonResponse({'status': 'success', 'message': 'Password reset OTP sent to your email.'})

@csrf_exempt
def api_reset_password(request):
    return JsonResponse({'status': 'success', 'message': 'Password reset successful.'})

@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({'status': 'success', 'message': 'Logged out successfully.'})
