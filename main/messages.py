import logging
import threading
from abc import ABC, abstractmethod
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from config import settings
from django.utils.translation import gettext_lazy


class BaseEmailNotification(EmailMultiAlternatives, ABC):
    template_name = 'template_name'
    default_from = settings.DEFAULT_FROM_EMAIL
    headers = {'From': 'noreplyexample@mail.com'}
    logger = logging.getLogger('main')

    def __init__(self, context, emails):
        super().__init__(
            subject=self.get_title(),
            from_email=self.default_from,
            to=emails,
            headers=self.headers,
            body=render_to_string(self.template_name, context=context)
        )
        self.content_subtype = "html"

    def inform(self):
        thread = threading.Thread(target=self.send)
        thread.start()

    @abstractmethod
    def get_title(self):
        raise NotImplementedError

    def send(self, fail_silently=False):
        try:
            super().send(fail_silently=fail_silently)
        except Exception as error:
            self.logger.error(self.message_error_text(error))

    def message_error_text(self, error):
        return f'{self=} message not sending. {error=}'


class BaseTelegramNotifications:
    pass


class ManagersEmailNotification(BaseEmailNotification, ABC):

    def __init__(self, context):
        super().__init__(context=context, emails=settings.MANAGERS_EMAILS)


class CustomersEmailNotification(BaseEmailNotification, ABC):

    def __init__(self, context, email):
        super().__init__(context=context, emails=[email])


class NewReferralRegisteredNotification(CustomersEmailNotification):
    template_name = 'template_name'

    def __init__(self, agent, referral):
        super().__init__(context={'referral': referral}, email=agent.email)

    def get_title(self):
        return gettext_lazy('Registered referral')


class EmailActivationNotification(CustomersEmailNotification):
    template_name = 'email_templates/activation_account_code.html'

    def __init__(self, email, code):
        super().__init__(context={'code': code},  email=email)

    def get_title(self):
        return gettext_lazy('Activation email')


class ActivatedSubscriptionNotification(CustomersEmailNotification):
    template_name = 'email_templates/subscription_activated.html'

    def __init__(self, subscription, email):
        super().__init__(context={'subscription': subscription}, email=email)

    def get_title(self):
        return gettext_lazy('Congratulations! Subscription activated!')


class ResetPasswordNotification(CustomersEmailNotification):
    template_name = 'email_templates/reset_password_code.html'

    def __init__(self, email, code,):
        super().__init__(context={'code': code}, email=email)

    def get_title(self):
        return gettext_lazy('Congratulations! Subscription activated!')



#
# class SubscriptionCreateNotification(BaseTelegramNotifications):
#     template_name = 'template_name'
#
#     def __init__(self, subscription):
#         super().__init__(context={'subscription': subscription})
#
#     def get_title(self):
#         return gettext_lazy('Subscribe order')
#
#
# class SubscriptionPaymentNotification(BaseTelegramNotifications):
#     template_name = 'email_templates/subscription_activated.html'
#
#     def __init__(self, subscription, email):
#         super().__init__(context={'subscription': subscription}, email=email)
#
#     def get_title(self):
#         return gettext_lazy('Congratulations! Subscription activated!')


# notf = SubscriptionCreateNotification(subscription, [config.settings.MANAGERS_EMAILS])
# notf.inform()
#
# notf = ReferralCreateNotification(referral, [request.user.agent.email])
# notf.inform()
