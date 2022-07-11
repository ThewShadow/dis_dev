from main.forms import *
from main.models import *
from config import settings


def base_context(request):
    common_context = dict()
    common_context['all_products'] = Product.objects.all()
    common_context['login_form'] = LoginForm()
    common_context['register_form'] = RegistrationForm()
    common_context['activation_email_form'] = VerifyEmailForm()
    common_context['questions_list'] = FAQ.objects.all()
    common_context['forget_pass_code_form'] = ResetPasswordVerifyForm()
    common_context['forget_pass_email_form'] = ResetPasswordForm()
    common_context['new_pass_form'] = NewPasswordForm()
    common_context['PAYPAL_CLIENT_ID'] = settings.PAYPAL_CLIENT_ID
    return common_context