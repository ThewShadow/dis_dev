from django.urls import reverse_lazy
from config import settings
import requests
import json
import urllib

GOOGLE_CLIENT_ID = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
GOOGLE_CLIENT_SECRET = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET

GOOGLE_USER_INFO_URI = 'https://www.googleapis.com/oauth2/v1/userinfo'
GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


def get_user_auth_token(code):
    payload = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': gen_login_callback_url(),
        'grant_type': 'authorization_code',
        'code': code
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(GOOGLE_TOKEN_URI, data=payload, headers=headers)
    response = json.loads(response.content)

    if 'access_token' in response:
        return response['access_token']
    else:
        return None


def get_user_info(token):

    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(GOOGLE_USER_INFO_URI, headers=headers)
    return json.loads(resp.content)


def gen_login_callback_url():
    path = reverse_lazy('service:google-auth2-complete')
    if settings.DEBUG:
        if settings.NGROK_DOMAIN:
            return f'{settings.NGROK_DOMAIN}{path}'
        else:
            return f'{settings.BASE_URL}{path}'
    else:
        return f'{settings.BASE_URL}{path}'


def gen_auth_url():
    parameters = {
        'redirect_uri': gen_login_callback_url(),
        'response_type': 'code',
        'client_id': GOOGLE_CLIENT_ID,
        'scope': ' '.join(GOOGLE_SCOPES),
    }

    query_string = urllib.parse.urlencode(parameters)
    url = GOOGLE_AUTH_URI + '?' + query_string

    return url
