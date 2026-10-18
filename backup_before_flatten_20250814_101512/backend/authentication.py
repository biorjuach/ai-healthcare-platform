from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json

def token_or_session_auth(view_func):
    """
    Custom decorator that handles both token and session authentication
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # First try session authentication (existing Django auth)
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        # If not authenticated via session, try token authentication
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Handle dummy token format: 'dummy-token-{user_id}'
            if token.startswith('dummy-token-'):
                try:
                    user_id = int(token.split('-')[-1])
                    user = User.objects.get(id=user_id)
                    request.user = user
                    return view_func(request, *args, **kwargs)
                except (ValueError, User.DoesNotExist):
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid token'
                    }, status=401)
        
        # If neither session nor token auth works, return unauthorized
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    return wrapper
