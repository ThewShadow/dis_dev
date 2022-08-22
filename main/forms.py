import datetime
from django.utils import timezone

from service import service
from . import models
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
            'email_verified'
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
        fields = ('offer', 'email', 'user', 'phone_number', 'service_password', 'is_exist_account')

        widgets = {
            'user': TextInput(attrs={
                'type': 'hidden'
            }),
        }


class SupportTaskCreateForm(ModelForm):
    img = forms.ImageField(required=False)
    pub_date = forms.DateTimeField(required=False)

    class Meta:
        model = SupportTask
        fields = ('description', 'pub_date', 'email', 'img')

        widgets = {
            'pub_date': DateTimeInput(attrs={
                'type': 'hidden'
            }),
        }

    def save(self, commit=True):
        task = super().save(commit=False)
        task.pub_date = timezone.now()
        if commit:
            task.save()
        return task


class ChangeUserInfoForm(ModelForm):

    class Meta:
        fields = ('username', 'email', )
        model = CustomUser

    def clean_email(self):
        new_email = self.cleaned_data.get('email')
        if self.instance.email == new_email:
            raise ValidationError('Email not changes')
        if not service.email_is_unique(self.instance.id, new_email):
            raise ValidationError('Email not uniq')
        return new_email

    def clean_username(self):
        new_username = self.cleaned_data.get('username')
        if self.instance.username == new_username:
            raise ValidationError('Username not change')
        return new_username


class ChangeSubscibeStatusForm(Form):
    sub_id = forms.IntegerField()


class SubscribeCreateForm(ModelForm):
    email = forms.EmailField()
    phone_number = PhoneNumberField()
    user_name = forms.CharField(max_length=250)
    service_password = forms.CharField(max_length=250, required=False)

    is_exist_account = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
                'class': 'checkbox-is-have-acc',
            }),
        initial=False)

    communication_preferences = forms.ChoiceField(
        choices=Subscription.communication_choices,
        widget=forms.RadioSelect,
        initial='wa',
    )

    class Meta:
        model = Subscription
        fields = (
            'email', 'phone_number', 'user_name', 'user', 'offer', 'service_password',
            'is_exist_account', 'communication_preferences'
        )

    def clean(self):
        super().clean()
        service_password = self.cleaned_data['service_password']
        is_exist_account = self.cleaned_data['is_exist_account']
        if len(service_password.strip()) == 0 \
                and is_exist_account:
            self.add_error('service_password', _('This field is required'))

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


class ChangePasswordForm(ModelForm):
    password_confirm = forms.CharField(max_length=250, required=True)

    class Meta:
        model = CustomUser
        fields = ('password', )

    def clean(self):
        super().clean()
        pass1 = self.cleaned_data.get('password')
        pass2 = self.cleaned_data.get('password_confirm')
        if not pass1 == pass2:
            self.add_error('password_confirm', _('Passwords do not match'))

    def save(self, commit=True):
        password = self.cleaned_data['password_confirm']
        self.instance.set_password(password)
        if commit:
            self.instance.save()
        return self.instance


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



