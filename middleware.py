import jwt
from django.conf import settings
from django.http import JsonResponse
import os

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.SHARED_SECRET_KEY = os.getenv('SHARED_SECRET_KEY')
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, self.SHARED_SECRET_KEY, algorithms=['HS256'])
                if payload['iss'] != 'main_server':
                    return JsonResponse({'error': 'Invalid token issuer'}, status=403)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired'}, status=403)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=403)
        else:
            return JsonResponse({'error': 'Authorization header missing'}, status=403)
        
        return self.get_response(request)
