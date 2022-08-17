from django.utils.translation import gettext_lazy
from main.models import *
from main.core import CustomersEmailNotification, ManagerTelegramMessage


class NewReferralRegisteredMessage(CustomersEmailNotification):
    template_name = 'template_name'

    def __init__(self, referral: CustomUser):
        super().__init__(context={'referral': referral}, email=referral.agent.email)

    def get_title(self):
        return gettext_lazy('Registered referral')


class SubscriptionPaymentMessage(ManagerTelegramMessage):
    template_name = 'messages_templates/paid_subscription_manager.html'

    def __init__(self, transaction: Transaction):
        super().__init__(context={'transaction': transaction})


class SubscriptionCreateMessage(ManagerTelegramMessage):
    template_name = 'messages_templates/telegram/new_subscription_manager.html'

    def __init__(self, subscription: Subscription):
        super().__init__(context={'subscription': subscription})


class EmailActivationCodeMessage(CustomersEmailNotification):
    template_name = 'email_templates/activation_account_code.html'

    def __init__(self, user_email: str, code: str):
        super().__init__(context={'code': code},  email=user_email)

    def get_title(self):
        return gettext_lazy('Activation email')


class SubscriptionActivatedSuccessMessage(CustomersEmailNotification):
    template_name = 'email_templates/subscription_activated.html'

    def __init__(self, subscription: Subscription):
        super().__init__(context={'subscription': subscription}, email=subscription.email)

    def get_title(self):
        return gettext_lazy('Congratulations! Subscription activated!')


class ResetPasswordCodeMessage(CustomersEmailNotification):
    template_name = 'email_templates/reset_password_code.html'

    def __init__(self, email: str, code: str):
        super().__init__(context={'code': code}, email=email)

    def get_title(self):
        return gettext_lazy('You reset code')

