from django.urls import reverse_lazy
from config import settings
import requests
import json
import urllib
import logging

logger = logging.getLogger('main')


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
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': gen_login_callback_url(),
        'grant_type': 'authorization_code',
        'code': code
    }

    response = requests.post(GOOGLE_TOKEN_URI, data=payload, headers=headers)

    try:
        response = json.loads(response.content)
    except json.JSONDecodeError:
        logger.warning(f'Google-Auth fail. response decode error. '
                       f'content: {str(response.content)}')

    try:
        return response['access_token']
    except KeyError:
        logger.warning(f'Google-Auth fail. access_token not found. '
                       f'response: {str(response)}')


def get_user_info(token):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(GOOGLE_USER_INFO_URI, headers=headers)

    try:
        return json.loads(resp.content)
    except json.JSONDecodeError:
        logger.warning(f'Google-Auth fail. response decode error. '
                       f'token: {str(token)}'
                       f'content: {str(resp.content)}')

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
            'access_type': 'offline'
    }

    query_string = urllib.parse.urlencode(parameters)
    url = GOOGLE_AUTH_URI + '?' + query_string

    return url
