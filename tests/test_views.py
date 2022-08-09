import time
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from main.models import CustomUser, CryptoWallet, Blockchain, Currency, Offer, Product, Rate, Subscription
import dataclasses
from django.core import mail
import re


@dataclasses.dataclass
class UserAuthData:
    email: str = 'vlad-dracula@gmail.com'
    password: str = 'dracula'


auth_data = UserAuthData()


class TestLogin(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            email=auth_data.email,
            password=auth_data.password)
        user.is_verified = True
        user.is_active = True
        user.save()

    def setUp(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        c.logout()

    def test_login(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        login_data = {
            'email': auth_data.email,
            'password': auth_data.password
        }
        resp = c.post(reverse('service:login'), data=login_data)
        self.assertEqual(resp.status_code, 200, msg=resp.json())

    def test_login_ajax(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        login = c.login(username=auth_data.email, password=auth_data.password)
        self.assertEqual(login, True, msg='login is fall')

        resp = c.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200, msg='User not authorized')

class TestRegistration(TestCase):
    register_data = {
        'username': 'tepes@13',
        'email': auth_data.email,
        'password': auth_data.password,
        'agreement': True,
    }

    @classmethod
    def setUpTestData(cls):
        agent = CustomUser.objects.create_user(email='www@gmail.com', password='123')
        agent.is_verified = True
        agent.is_active = True
        agent.is_superuser = True
        agent.save()

        agent1 = CustomUser.objects.create_user(email='www1@gmail.com', password='123')
        agent1.is_verified = True
        agent1.is_active = True
        agent1.is_superuser = True
        agent1.save()

    def setUp(self):
        pass

    def test_registration_ajax(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        c.cookies.load({'ref_link': '0000002'})

        resp = c.post(reverse('service:registration'), data=self.register_data)
        self.assertEqual(resp.status_code, 201, msg=f'Register fail {resp.json()}')

        # mail can send a few seconds
        time.sleep(5)

        self.assertEqual(len(mail.outbox), 1)

        activation_email_message = mail.outbox[0]
        self.assertEqual(activation_email_message.subject, 'Activation email', msg='Activation message not send')

        code = re.search(r'[0-9]{3,}', activation_email_message.body).group()
        self.assertIsNotNone(code, msg=f'Activation code not found {code=}')

        resp = c.post(reverse('service:activation_email'), {'activation_code': code})
        self.assertEqual(resp.status_code, 200, msg=f'Email not activated {code=}')

        resp = c.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200, msg='User not logged after sign up')

        user = CustomUser.objects.filter(email=auth_data.email).first()
        self.assertEqual(type(user.agent), CustomUser, msg='User agent not set')
        self.assertEqual(user.agent.email, 'www1@gmail.com', msg='User agent different')

class TestCryptoPayment(TestCase):
    @classmethod
    def setUpTestData(cls):
        bl = Blockchain()
        bl.blockchain_name = 'Blockchain BTC network'
        bl.save()

        curr = Currency()
        curr.name = 'Bitcoin'
        curr.code = 'BTC'
        curr.crypto = True
        curr.save()

        cw = CryptoWallet()
        cw.blockchain = bl
        cw.currency = curr
        cw.paycode = 'q4fw5etv5ewgcwe5cfumow'
        cw.save()

        product = Product()
        product.name = 'Netflix'
        product.description = 'xxx'
        product.slug = 'xxx'
        product.save()

        rate = Rate()
        rate.name = 'mounth'
        rate.count = 12
        rate.slug = 'xxx'
        rate.save()

        offer = Offer()
        offer.product = product
        offer.price = 40
        offer.name = 'basic'
        offer.currency = curr
        offer.description = 'xxx'
        offer.rate = rate
        offer.save()

        user = CustomUser.objects.create_user(
            email=auth_data.email,
            password=auth_data.password)
        user.is_verified = True
        user.is_active = True
        user.save()

        subscr = Subscription()
        subscr.user = user
        subscr.email = auth_data.email
        subscr.service_password = 'xxx'
        subscr.offer = offer
        subscr.user_name = 'xxx'
        subscr.phone_number = '1231231232'
        subscr.save()

    def setUp(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        pass

    def test_payment_view(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        session = c.session
        session['current_sub_id'] = 1
        session.save()
        resp = c.get(reverse('crypto-pay'))
        self.assertEqual(resp.status_code, 200)

    def test_create_payment(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        json = {
            'wallet_id': 1,
        }

        session = c.session
        session['current_sub_id'] = 1
        session.save()
        resp = c.post(reverse('service:crypto-pay-create'), data=json)

        self.assertEqual(resp.status_code, 200)
        import json
        resp_data = json.loads(resp.content.decode())
        payment_data = resp_data['payment_data']
        self.assertIsNotNone(payment_data['paycode'])
        self.assertIsNotNone(payment_data['qrcode'])
        self.assertIsNotNone(payment_data['price'])
        self.assertIsNotNone(payment_data['blockchain'])
        self.assertIsNotNone(payment_data['currency'])
