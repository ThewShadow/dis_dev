from config import settings
import random
from main import models
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.core.mail import send_mail


def gen_verify_code():
    default_code_length = 6
    code_length = default_code_length if 'VERIFY_CODE_LENGTH' not in dir(settings) \
        else settings.VERIFY_CODE_LENGTH

    result = ''
    for i in range(code_length):
        result += str(random.randint(3, 9))
    return result


def send_activation_account_code(code, to):
    from_email = settings.EMAIL_HOST_USER
    subject = _('Activation email',)
    html_content = render_to_string('email_templates/activation_account_code.html',
                                    {'code': code})
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()


def send_reset_password_code(code, to):
    from_email = settings.EMAIL_HOST_USER
    subject = _('Password reset code',)
    html_content = render_to_string('email_templates/reset_password_code.html',
                                    {'code': code})
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()


def user_email_uniq(user, email):
    return not models.CustomUser.objects\
        .exclude(id=user.id)\
        .filter(email=email)\
        .exists()


def change_profile_info(request, form):
    user = request.user

    new_username = form.cleaned_data.get('username')
    new_email = form.cleaned_data.get('email')

    if user.email == new_email \
            and user.username == new_username:
        return

    if not user_email_uniq(user, new_email):
        raise Exception('EmailNotUniq')

    user.email = new_email
    user.username = new_username

    try:
        user.save()
    except Exception as excp:
        raise Exception('UserSaveError')

    return True


def send_support_task(task_id):
    task = models.SupportTask.objects.get(id=task_id)
    send_mail(
        task.title,
        task.text,
        'noreplyexample@mail.com',
        ['zvichayniy.vick@gmail.com'],
        fail_silently=False
    )

