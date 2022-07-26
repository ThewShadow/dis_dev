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

logger = logging.getLogger('main')

try:
    bot = TeleBot(TELEGRAM_BOT_API_KEY)
except telebot.apihelper.ApiHTTPException as e:
    logger.error(f'Telegram bot not created. error: {e}')


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=250)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    social_sign_up = models.BooleanField(default=False)

    agent = models.ForeignKey('CustomUser', on_delete=models.SET_DEFAULT, default=1)

    def __str__(self):
        return self.email

    def set_agent(self, agent_id):
        if not agent_id:
            return
        try:
            self.agent = CustomUser.objects.get(id=agent_id.lstrip('0'))
        except CustomUser.DoesNotExist:
            logger.warning(f'Agent not found. ref_link: {agent_id.lstrip("0")}')


class Rate(models.Model):
    name = models.CharField(max_length=200, default='')
    count = models.IntegerField()
    slug = models.SlugField(default='')

    def __str__(self):
        return f'{self.count} {self.name}'


class Currency(models.Model):
    name = models.CharField(max_length=40, default='')
    code = models.CharField(max_length=4, default='')

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
    rate = models.ForeignKey('Rate', on_delete=models.CASCADE, null=True)
    price = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE, null=True)
    description = models.TextField(null=True)
    features = models.ManyToManyField('Feature')

    def __str__(self):
        return f'{self.product.name} | {self.name} | {self.rate} | {self.price} {self.currency.code}'


class Product(models.Model):
    name = models.CharField(max_length=200, default='')
    slug = models.SlugField(default='')
    multi_plane = models.BooleanField(default=False)
    description = models.TextField(null=True)
    background_color = models.CharField(max_length=12)
    icon = models.FileField(upload_to='media/products/', null=True, blank=True, default=None)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, null=True)
    email = models.EmailField(max_length=250)
    phone_number = PhoneNumberField(null=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True)
    user_name = models.CharField(max_length=250, null=True)
    paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    service_password = models.CharField(max_length=20)

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
            {'subscription': self})

        msg = EmailMultiAlternatives(subject, html_content, config.settings.DEFAULT_FROM_EMAIL,
                                     to=to,  headers={'From': 'noreplyexample@mail.com'})
        msg.content_subtype = "html"
        try:
            msg.send()
        except (smtplib.SMTPDataError, smtplib.SMTPAuthenticationError) as e:
            logger.error(f'Subscription activate message not sent. error: {e}')

    def set_service_password(self, length=7):
        chars = list(string.ascii_letters + string.digits)
        random.shuffle(chars)

        password = []
        for i in range(length):
            password.append(random.choice(chars))

        random.shuffle(password)
        self.service_password = "".join(password)


class SupportTask(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    text = models.TextField()
    pub_date = models.DateTimeField()
    email = models.EmailField(default='')

    def __str__(self):
        return f'{self.pub_date} {self.user} {self.title}'


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


def send_to_telegram(message):
    from config.settings import TELEGRAM_GROUP_MANAGERS_ID as chat_id

    try:
        bot.send_message(chat_id=chat_id, text=message)
    except telebot.apihelper.ApiHTTPException as e:
        logger.error(f'Telegram message not sent. error: {e}')
