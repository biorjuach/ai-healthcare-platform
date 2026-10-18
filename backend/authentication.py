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
        import logging
        logger = logging.getLogger(__name__)
        
        # Debug logging
        logger.info(f"Token or session auth: User authenticated: {request.user.is_authenticated}")
        logger.info(f"Token or session auth: Authorization header: {request.headers.get('Authorization', 'Not present')}")
        
        # First try session authentication (existing Django auth)
        if request.user.is_authenticated:
            logger.info(f"Token or session auth: Using session authentication for user {request.user.username}")
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
            
            # Handle JWT tokens
            else:
                try:
                    from rest_framework_simplejwt.tokens import AccessToken
                    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                    
                    logger.info(f"Token or session auth: Attempting JWT token validation")
                    
                    # Decode the JWT token
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    user = User.objects.get(id=user_id)
                    request.user = user
                    logger.info(f"Token or session auth: JWT authentication successful for user {user.username}")
                    return view_func(request, *args, **kwargs)
                except (InvalidToken, TokenError, User.DoesNotExist) as e:
                    logger.error(f"Token or session auth: JWT authentication failed: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid or expired token'
                    }, status=401)
        
        # If neither session nor token auth works, return unauthorized
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    return wrapper
