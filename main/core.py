import logging
import threading
from abc import ABC, abstractmethod
import telebot
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy
from config import settings


class BaseNotification(ABC):
    template_name = 'template_name'
    logger = logging.getLogger('main')

    def inform(self):
        thread = threading.Thread(target=self.notify_handler)
        thread.start()

    @staticmethod
    def message_error_text(error):
        return f'Message not sending. {error=}'

    @staticmethod
    def silence(func):
        def wrap(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as error:
                BaseNotification.logger.error(
                    BaseNotification.message_error_text(error)
                )

        return wrap

    @abstractmethod
    def notify_handler(self):
        pass


# TELEGRAM
class TelegramNotification(BaseNotification, telebot.TeleBot):
    def __init__(self, chat_id: str, context: (object, dict)):
        super().__init__(settings.TELEGRAM_BOT_API_KEY)
        self.chat_id = chat_id
        self.text = render_to_string(template_name=self.template_name, context=context)

    @BaseNotification.silence
    def notify_handler(self):
        print(dir(self))
        self.send_message(chat_id=self.chat_id, text=self.text, parse_mode='html')


class ManagerTelegramMessage(TelegramNotification, ABC):
    managers_chat_id = settings.TELEGRAM_GROUP_MANAGERS_ID

    def __init__(self, context: (dict, object)):
        super().__init__(chat_id=self.managers_chat_id, context=context)


# EMAIL
class EmailNotification(BaseNotification, EmailMultiAlternatives, ABC):
    default_from = settings.DEFAULT_FROM_EMAIL
    headers = {'From': 'noreplyexample@mail.com'}

    def __init__(self, context, email):
        if isinstance(email, str):
            emails = [email]
        else:
            emails = email

        super().__init__(
            subject=self.get_title(),
            from_email=self.default_from,
            to=emails,
            headers=self.headers,
            body=render_to_string(template_name=self.template_name, context=context)
        )
        self.content_subtype = "html"

    @BaseNotification.silence
    def notify_handler(self):
        self.send()

    @abstractmethod
    def get_title(self):
        return gettext_lazy('Title')


class ManagersEmailMessage(EmailNotification, ABC):
    managers_emails = settings.MANAGERS_EMAILS

    def __init__(self, context):
        super().__init__(context=context, email=self.managers_emails)


class CustomersEmailNotification(EmailNotification, ABC):

    def __init__(self, context, email):
        super().__init__(context=context, email=[email])
