import telebot
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.template.loader import render_to_string
import config.settings
from .managers import CustomUserManager
from django.core.mail import EmailMultiAlternatives
import logging
import smtplib
from telebot import TeleBot
from config.settings import TELEGRAM_BOT_API_KEY
import string
import random
from django.core.mail import send_mail
from django.db.models import F

logger = logging.getLogger('main')

try:
    bot = TeleBot(TELEGRAM_BOT_API_KEY)
except telebot.apihelper.ApiHTTPException as e:
    logger.error(f'Telegram bot not created. error: {e}')


class CustomUser(AbstractBaseUser, PermissionsMixin):
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=250)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)

    email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    social_sign_up = models.BooleanField(default=False)

    agent = models.ForeignKey(
        'self',
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='referrals')

    def __str__(self):
        return self.email

    def set_agent(self, agent_id):
        if not agent_id or not isinstance(agent_id, int):
            return

        try:
            agent = CustomUser.objects.get(id=agent_id)
        except CustomUser.DoesNotExist:
            logger.warning(f'Agent not found. ref_link: {agent_id=}')
            return

        self.agent = agent


class Rate(models.Model):
    name = models.CharField(max_length=200, default='')
    count = models.IntegerField()
    slug = models.SlugField(default='')

    def __str__(self):
        return f'{self.count} {self.name}'


class Currency(models.Model):
    name = models.CharField(max_length=40, default='')
    code = models.CharField(max_length=4, default='')
    crypto = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.code})'


class FAQ(models.Model):
    title = models.CharField(max_length=200, default='')
    answer = models.TextField(null=True)

    def __str__(self):
        return self.title


class Feature(models.Model):
    name = models.TextField(verbose_name='product features', null=True)

    def __str__(self):
        return self.name


class Offer(models.Model):
    name = models.CharField(max_length=200, default='')
    rate = models.ForeignKey('Rate', on_delete=models.SET_NULL, null=True)
    price = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    features = models.ManyToManyField('Feature')

    def __str__(self):
        return f'{self.product.name} | {self.name} | {self.rate} | {self.price} {self.currency.code}'

    @classmethod
    def get_price_by_id(cls, id):
        return cls.objects.filter(id=id).first().price

class Product(models.Model):
    name = models.CharField(max_length=200, default='')
    slug = models.SlugField(default='')
    multi_plane = models.BooleanField(default=False)
    description = models.TextField(null=True)
    background_color = models.CharField(max_length=12)
    icon = models.FileField(upload_to='media/products/', null=True, blank=True, default=None)
    allow_existing_accounts = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    offer = models.ForeignKey('Offer', on_delete=models.PROTECT, null=True)
    email = models.EmailField(max_length=250)
    phone_number = PhoneNumberField(null=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True)
    user_name = models.CharField(max_length=250, null=True)
    paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    service_password = models.CharField(max_length=250)
    is_exist_account = models.BooleanField(default=False)

    communication_choices = [
        ('email', 'Email'),
        ('wa', 'Whatsapp')
    ]
    communication_preferences = models.CharField(
        max_length=250,
        choices=communication_choices,
        default='email'
    )


    def __str__(self):
        return f'{self.user} - {self.offer}'

    def notify_managers(self):
        message = render_to_string(
            'messages_templates/telegram/new_subscription_manager.html',
            {'subscription': self,
             'order_date': self.order_date.strftime("%d/%m/%y %H:%M")})
        send_to_telegram(message)

    def notify_customer(self):
        subject, to = 'Subscription activated!', [self.email]
        html_content = render_to_string(
            'email_templates/subscription_activated.html',
            {
                'subscription': self,
                'service_password': self.service_password
            }
        )

        msg = EmailMultiAlternatives(subject, html_content, config.settings.DEFAULT_FROM_EMAIL,
                                     to=to,  headers={'From': 'noreplyexample@mail.com'})
        msg.content_subtype = "html"
        try:
            msg.send()
        except (smtplib.SMTPDataError, smtplib.SMTPAuthenticationError) as e:
            logger.error(f'Subscription activate message not sent. error: {e}')

    def set_service_password(self, length=7):
        if self.is_exist_account or self.service_password:
            return

        chars = list(string.ascii_letters + string.digits)
        random.shuffle(chars)

        password = []
        for i in range(length):
            password.append(random.choice(chars))

        random.shuffle(password)
        self.service_password = "".join(password)


class SupportTask(models.Model):
    description = models.TextField()
    pub_date = models.DateTimeField()
    email = models.EmailField()
    img = models.ImageField(null=True)

    def __str__(self):
        return f'{self.pub_date} {self.email}'

    def mail_managers(self):
        title = f'Customer appeal from {self.email}'

        msg = EmailMultiAlternatives(
            title,
            self.description,
            config.settings.DEFAULT_FROM_EMAIL,
            to=config.settings.MANAGERS_EMAILS
        )

        image = open(self.img.url, 'rb')
        msg.attach(self.img, image)
        try:
            msg.send()
        except (smtplib.SMTPDataError, smtplib.SMTPAuthenticationError) as e:
            logger.error(f'Customer appeal message not sent. error: {e}')



class Transaction(models.Model):
    transaction_id = models.CharField(max_length=250)
    date_create = models.DateTimeField()
    subscription = models.ForeignKey('Subscription',
        on_delete=models.CASCADE)

    comment = models.TextField(null=True, blank=True)

    paytypes = [
        ('paypal', 'PayPal',),
        ('crypto', 'Crypto Wallet',)
    ]
    pay_type = models.CharField(max_length=255, choices=paytypes)

    def __str__(self):
        return self.transaction_id

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.notify_managers()

    def notify_managers(self):
        message = render_to_string(
            'messages_templates/telegram/paid_subscription_manager.html',
            {'subscription': self.subscription,
             'transaction': self})
        send_to_telegram(message)


class Blockchain(models.Model):
    blockchain_name = models.CharField(max_length=250)

    def __str__(self):
        return self.blockchain_name

class CryptoWallet(models.Model):
    blockchain = models.ForeignKey('Blockchain', on_delete=models.PROTECT, null=True, related_name='wallets')
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, related_name='crypto_wallets')
    paycode = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.blockchain} | {self.currency}'

    @staticmethod
    def get_wallets_by_currency_id(currency_id) -> list:
        wallets = CryptoWallet.objects.filter(
            currency__id=currency_id
        ).prefetch_related(
            'blockchain', 'currency'
        ).annotate(
            blockchain_name=F('blockchain__blockchain_name')
        ).values(
            'blockchain_name', 'id',
        )
        return list(wallets)


def send_to_telegram(message):
    from config.settings import TELEGRAM_GROUP_MANAGERS_ID as chat_id

    try:
        bot.send_message(chat_id=chat_id, text=message)
    except telebot.apihelper.ApiHTTPException as e:
        logger.error(f'Telegram message not sent. error: {e}')
