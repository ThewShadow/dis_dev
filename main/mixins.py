from main.forms import *
from main.models import *


def base_context_processor():
    common_context = dict()
    common_context['all_products'] = Product.objects.all()
    common_context['login_form'] = LoginForm()
    common_context['register_form'] = RegistrationForm()
    common_context['activation_email_form'] = VerifyEmailForm()
    common_context['questions_list'] = FAQ.objects.all()
    common_context['forget_pass_code_form'] = ResetPasswordVerifyForm()
    common_context['forget_pass_email_form'] = ResetPasswordForm()
    common_context['new_pass_form'] = NewPasswordForm()

    return common_context


class BaseContextMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        common = BaseContextMixin._get_base_context()
        context.update(common)
        return context

    @staticmethod
    def _get_base_context():
        common_context = dict()
        common_context['all_products'] = Product.objects.all()
        common_context['login_form'] = LoginForm()
        common_context['register_form'] = RegistrationForm()
        common_context['activation_email_form'] = VerifyEmailForm()
        common_context['questions_list'] = FAQ.objects.all()
        common_context['forget_pass_code_form'] = ResetPasswordVerifyForm()
        common_context['forget_pass_email_form'] = ResetPasswordForm()
        common_context['new_pass_form'] = NewPasswordForm()

        return common_context

