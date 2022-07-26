from .models import Subscription, SupportTask
from django.forms import ModelForm, DateTimeInput, TextInput, NumberInput, Form
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import Transaction
import logging
from phonenumber_field.formfields import PhoneNumberField

logger = logging.getLogger('main')


class CustomUserSocialCreationForm(ModelForm):

    ref_link = forms.CharField(max_length=255, required=False)

    class Meta(UserCreationForm):
        model = CustomUser
        fields = (
            'email',
            'username',
            'social_sign_up',
            'is_active',
            'is_verified'
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("Email already exists"))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_agent(self.cleaned_data["ref_link"])
        if commit:
            user.save()
        return user


class CustomUserCreationForm(ModelForm):

    ref_link = forms.CharField(max_length=255, required=False)
    agreement = forms.BooleanField(required=True)

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'username', 'password')

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("Email already exists"))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.set_agent(self.cleaned_data["ref_link"])

        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class SubscribeForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ('offer', 'email', 'user', 'phone_number',)

        widgets = {
            'user': TextInput(attrs={
                'type': 'hidden'
            }),
        }


class SupportCreateTaskForm(ModelForm):
    class Meta:
        model = SupportTask
        fields = ('user', 'title', 'text', 'pub_date', 'email',)

        widgets = {
            'pub_date': DateTimeInput(attrs={
                'type': 'hidden'
            }),
            'user': TextInput(attrs={
                'type': 'hidden'
            }),
        }


class ChangeUserInfoForm(Form):
    username = forms.CharField(max_length=250, label='Your name')
    email = forms.EmailField(max_length=250)

    class Meta:
        fields = ('username', 'email', )


class ChangeSubscibeStatusForm(Form):
    sub_id = forms.IntegerField()


class SubscribeCreateForm(ModelForm):
    email = forms.EmailField()
    phone_number = PhoneNumberField()
    user_name = forms.CharField(max_length=250)

    class Meta:
        model = Subscription
        fields = (
            'email',
            'phone_number',
            'user_name',
            'user',
            'offer',
        )

    def save(self, commit=True):
        subscription = super().save(commit=False)
        subscription.set_service_password()

        if commit:
            subscription.save()
        return subscription


class LoginForm(Form):
    email = forms.EmailField(max_length=250, required=True)
    password = forms.CharField(max_length=250, required=True)

    def clean_email(self):

        email = self.cleaned_data['email']
        users = CustomUser.objects.filter(email=email)

        if not users.exists():
            raise ValidationError(_("User with this email does not exist"))

        return email


class RegistrationForm(Form):
    username = forms.CharField(max_length=250, required=True)
    email = forms.EmailField(max_length=250, required=True)
    password = forms.CharField(max_length=250, required=True)


class VerifyEmailForm(Form):
    activation_code = forms.CharField(required=True)


class ResetPasswordForm(Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_('User not exist'))
        return email


class ResetPasswordVerifyForm(Form):
    verify_code = forms.CharField(max_length=6, required=True)


class NewPasswordForm(Form):
    password1 = forms.CharField(max_length=250, required=True)
    password2 = forms.CharField(max_length=250, required=True)

    def clean(self):
        super().clean()
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if not pass1 == pass2:
            self.add_error('password2', _('Passwords do not match'))


class TransactionForm(ModelForm):

    class Meta:
        model = Transaction
        fields = (
            'transaction_id',
            'date_create',
            'subscription',
            'pay_type',
            'comment'
        )



