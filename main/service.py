from .models import Subscription
from .models import Offer
from .models import SupportTask
from django.core.mail import send_mail
import logging
import json
import requests
from config import settings
import random


logger = logging.getLogger(__name__)


def gen_verify_code():
    default_code_length = 6
    code_length = default_code_length if 'VERIFY_CODE_LENGTH' not in dir(settings) else settings.VERIFY_CODE_LENGTH
    result = ''
    for i in range(code_length):
        result += str(random.randint(3, 9))
    return result

def gen_crypto_pay_link(currency, blockchain):
    return '11234234234234323423'

def get_user_token(code):
    GOOGLE_CLIENT_SECRET = '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'
    GOOGLE_CLIENT_ID = '15243234059-ts6k6h4u5bd71q7ssimapkfifec7h5po.apps.googleusercontent.com'
    GOOGLE_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'

    payload = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': gen_collback_url(),
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
    GOOGLE_USER_INFO_URI = 'https://www.googleapis.com/oauth2/v1/userinfo'
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(GOOGLE_USER_INFO_URI, headers=headers)
    return json.loads(resp.content)

def gen_collback_url():
    return 'https://8f7b-46-118-172-5.eu.ngrok.io/accounts/social/login_complete/'



def get_customer_subscriptions(customer_id):
    try:
        return Subscription.objects.filter(user__id=customer_id) or []
    except Exception as e:
        logger.error(e)


def get_offers_by_slug(slug):
    try:
        return Offer.objects.filter(product__slug=slug)
    except Exception as e:
        logger.error(e)



def send_support_task(task_id):
    try:
        task = SupportTask.objects.get(id=task_id)
        send_mail(
            task.title,
            task.text,
            'noreplyexample@mail.com',
            ['zvichayniy.vick@gmail.com'],
            fail_silently=False
        )
    except Exception as e:
        logger.error(e)


def notify_managers_of_new_subscription(subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Exception as e:
        logger.error(f'subscription not found {e}')
    else:
        try:
            send_mail(
                'new subscription',
                str(subscription),
                'noreplyexample@mail.com',
                ['zvichayniy.vick@gmail.com'],
                fail_silently=False
            )
        except Exception as e:
            logger.error(f'notify_managers error {e}')

def check_payment():
    pass


def gen_refer_link(user):
    pass


def create_payment(data):
    pass


def send_status_change_notification(user, data):
    pass


def senf_notification_new_subscription(data):
    pass


def get_refer_link(user):
    pass


