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


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=250)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


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


class Offer(models.Model):
    name = models.CharField(max_length=200, default='')
    rate = models.ForeignKey('Rate', on_delete=models.CASCADE, null=True)
    price = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return f'{self.product.name} - {self.name} - {self.rate}: {self.price} {self.currency.code}'


class Product(models.Model):
    name = models.CharField(max_length=200, default='')
    slug = models.SlugField(default='')
    multi_plane = models.BooleanField(default=False)
    description = models.TextField(null=True)
    background_color = models.CharField(max_length=12)
    icon = models.FileField(upload_to='media/products/', null=True, blank=True, default=None)

    def __str__(self):
        return self.name


class PaymentType(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, null=True)
    email = models.EmailField(max_length=250)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, null=True)
    phone_number = PhoneNumberField(null=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True)
    user_name = models.CharField(max_length=250, null=True)
    paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    STATUSES = [
        (1, 'being processed'),
        (2, 'done'),
        (3, 'canceled'),
    ]
    status = models.IntegerField(
        choices=STATUSES,
        default=1,
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
            {'subscription': self})

        msg = EmailMultiAlternatives(subject, html_content, config.settings.DEFAULT_FROM_EMAIL,
                                     to=to,  headers={'From': 'noreplyexample@mail.com'})
        msg.content_subtype = "html"
        msg.send()


class SupportTask(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    text = models.TextField()
    pub_date = models.DateTimeField()
    email = models.EmailField(default='')

    def __str__(self):
        return f'{self.pub_date} {self.user} {self.title}'


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=250, null=True)
    date_create = models.DateTimeField()
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE)

    def notify_managers(self):
        message = render_to_string(
            'messages_templates/telegram/paid_subscription_manager.html',
            {'subscription': self.subscription,
             'transaction': self})
        send_to_telegram(message)


def send_to_telegram(message):
    from telebot import TeleBot
    from config.settings import TELEGRAM_BOT_API_KEY
    from config.settings import TELEGRAM_GROUP_MANAGERS_ID as chat_id
    bot = TeleBot(TELEGRAM_BOT_API_KEY)
    bot.send_message(chat_id=chat_id, text=message)


