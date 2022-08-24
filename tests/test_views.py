import time
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
import service.service
from main.models import CustomUser, CryptoWallet, Blockchain, Currency, Offer, Product, Rate, Subscription
import dataclasses
from django.core import mail
import re
import json


@dataclasses.dataclass
class UserAuthData:
    email: str = 'vlad-dracula@gmail.com'
    password: str = 'dracula'


auth_data = UserAuthData()


class TestProfile(TestCase):
    current_user_id = None

    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(email=auth_data.email, password=auth_data.password)
        user.email_verified = True
        user.is_active = True
        user.username = 'tepes'
        user.save()
        cls.current_user_id = user.id

    def test_change_user_info(self):
        new_username = 'NewUserName'
        new_email = 'newemail@gmail.com'

        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        c.login(username=auth_data.email, password=auth_data.password)

        resp = c.post(reverse('my_info'), data={'username': new_username, 'email': new_email})
        self.assertEqual(resp.status_code, 200, msg='Change user info fail. Error Request.')

        user = CustomUser.objects.get(id=self.current_user_id)
        self.assertEqual(user.username, new_username)
        self.assertEqual(user.email, new_email)


class TestLogin(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(email=auth_data.email, password=auth_data.password)
        user.email_verified = True
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

    def test_checks_access_profile(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        c.login(username=auth_data.email, password=auth_data.password)

        resp = c.get(reverse('my_info'))
        self.assertEqual(resp.status_code, 200, msg='User not authorized')

    def test_logout(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        c.login(username=auth_data.email, password=auth_data.password)
        resp = c.post(reverse('logout'))
        self.assertEqual(resp.status_code, 302, msg='logout is fail')


class TestRegistration(TestCase):

    register_data = {
        'username': 'tepes@13',
        'email': auth_data.email,
        'password': auth_data.password,
        'agreement': True,
    }

    @classmethod
    def setUpTestData(cls):
        base_agent = CustomUser.objects.create_user(email='www@gmail.com', password='123')
        base_agent.email_verified = True
        base_agent.is_active = True
        base_agent.is_superuser = True
        base_agent.save()

        agent1 = CustomUser.objects.create_user(email='www1@gmail.com', password='123')
        agent1.email_verified = True
        agent1.is_active = True
        agent1.is_superuser = True
        agent1.save()

    def setUp(self):
        mail.outbox.clear()

    def test_checks_the_base_registration_of_the_user(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        c.cookies.load({'ref_link': '0000002'})

        resp = c.post(reverse('service:registration'), data=self.register_data)
        self.assertEqual(resp.status_code, 201, msg=f'Register fail {resp.json()}')

        # mail can send a few seconds
        time.sleep(5)

        self.assertEqual(len(mail.outbox), 1, msg='Activation message not send')

        title = mail.outbox[0].subject
        self.assertEqual(title, 'Activation email', msg='Activation message not send')

        code = find_code_in_letter(mail.outbox[0].body)
        self.assertIsNotNone(code, msg=f'Activation code not found {code=}')

        resp = c.post(reverse('service:activation_email'), {'activation_code': code})
        self.assertEqual(resp.status_code, 200, msg=f'Email not activated {code=}')

        resp = c.get(reverse('my_info'))
        self.assertEqual(resp.status_code, 200, msg='User not logged after sign up')

        user = CustomUser.objects.filter(email=auth_data.email).first()
        self.assertEqual(type(user.agent), CustomUser, msg='User agent not set')
        self.assertEqual(user.agent.email, 'www1@gmail.com', msg='User agent different')

        self.assertEqual(len(mail.outbox), 2, msg='Letter about registration referral not sent')

        title = mail.outbox[1].subject
        self.assertEqual(title, 'Registration Referral', msg='Letter about registration email not sent')


def find_code_in_letter(letter: str):
    return re.search(r'[0-9]{3,}', letter).group()


class TestResetPassword(TestCase):
    reset_pass_data = {
        'email': auth_data.email,
    }

    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            email=auth_data.email,
            password=auth_data.password)
        user.email_verified = True
        user.is_active = True
        user.save()

    def setUp(self):
        mail.outbox.clear()

    def test_reset_password_success(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        resp = c.post(reverse('service:reset_pass'), data=self.reset_pass_data)
        json_response = resp.json()
        self.assertEqual(resp.status_code, 200, msg=f'Register fail {resp.json()} {json_response=}')

        # mail can send a few seconds
        time.sleep(5)

        # code sending ?
        self.assertEqual(len(mail.outbox), 1, msg='Reset password message not send')

        title = mail.outbox[0].subject
        self.assertEqual(title, 'You reset code', msg='Resset cod message not send')

        code = find_code_in_letter(mail.outbox[0].body)
        self.assertIsNotNone(code, msg=f'Resset code not found in letter{code=}')

        resp = c.post(reverse('service:reset_pass_confirm'), {'verify_code': code})
        json_response = resp.json()
        self.assertEqual(resp.status_code, 200, msg=f'Email not activated {code=} {json_response=}')

        new_pass = service.service.gen_verify_code()
        resp = c.post(reverse('service:reset_pass_complete'), {'password': new_pass, 'password_confirm': new_pass})

        json_response = resp.json()
        self.assertEqual(resp.status_code, 200, msg=f'Password not restored {new_pass=} {json_response=}')

        resp = c.post(reverse('service:login'), data={'email': auth_data.email, 'password': new_pass})
        self.assertEqual(resp.status_code, 200, msg=f'Login fail after reset password {resp.json()}')

    def test_fail_when_code_incorrect(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        resp = c.post(reverse('service:reset_pass'), data=self.reset_pass_data)
        json_response = resp.json()
        self.assertEqual(resp.status_code, 200, msg=f'Reset password start fail {json_response=}')

        # mail can send a few seconds
        time.sleep(5)

        # code sending ?
        self.assertEqual(len(mail.outbox), 1)

        user_email = mail.outbox[0].subject
        self.assertEqual(user_email, 'You reset code', msg='Resset cod message not send')

        true_code = find_code_in_letter(mail.outbox[0].body)
        self.assertIsNotNone(true_code, msg=f'Resset code not found in letter{true_code=}')

        fake_code = service.service.gen_verify_code()

        resp = c.post(reverse('service:reset_pass_confirm'), {'verify_code': fake_code})
        json_response = resp.json()

        self.assertNotEqual(resp.status_code, 200, msg=f'Reset password started with fake code '
                                                       f'{fake_code=} {true_code=} {json_response=}')

        fake_pass1 = service.service.gen_verify_code()
        fake_pass2 = fake_pass1

        resp = c.post(reverse('service:reset_pass_complete'), {'password1': fake_pass1, 'password2': fake_pass2})
        json_response = resp.json()

        self.assertNotEqual(resp.status_code, 200, msg=f'Password changed with incorrect password '
                                                       f'{fake_pass1=} {fake_pass2=} {json_response=}')


class TestCryptoPayment(TestCase):

    @classmethod
    def setUpTestData(cls):
        bl = Blockchain(blockchain_name='Blockchain BTC network')
        bl.save()

        curr = Currency(name='Bitcoin', code='BTC', crypto=True)
        curr.save()

        cw = CryptoWallet(blockchain=bl, currency=curr, paycode='q4fw5etv5ewgcwe5cfumow')
        cw.save()

        product = Product(name='Netflix', description='xxx', slug='xxx')
        product.save()

        rate = Rate(name='mouth', count=12, slug='xxx')
        rate.save()

        offer = Offer(product=product, price=40, name='Basic', currency=curr, description='xxx', rate=rate)
        offer.save()

        user = CustomUser.objects.create_user(email=auth_data.email, password=auth_data.password)
        user.email_verified = True
        user.is_active = True
        user.save()

        subscription = Subscription()
        subscription.user = user
        subscription.email = auth_data.email
        subscription.service_password = 'xxx'
        subscription.offer = offer
        subscription.user_name = 'xxx'
        subscription.phone_number = '1231231232'
        subscription.save()

    def test_payment_view(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')

        session = c.session
        session['current_sub_id'] = 1
        session.save()
        resp = c.get(reverse('crypto-pay'))
        self.assertEqual(resp.status_code, 200)

    def test_create_payment(self):
        c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        data_wallet = {
            'wallet_id': 1,
        }

        session = c.session
        session['current_sub_id'] = 1
        session.save()
        resp = c.post(reverse('service:crypto-pay-create'), data=data_wallet)

        self.assertEqual(resp.status_code, 200)

        resp_data = json.loads(resp.content.decode())
        payment_data = resp_data['payment_data']

        self.assertIsNotNone(payment_data['paycode'])
        self.assertIsNotNone(payment_data['qrcode'])
        self.assertIsNotNone(payment_data['price'])
        self.assertIsNotNone(payment_data['blockchain'])
        self.assertIsNotNone(payment_data['currency'])
