from django.forms import ModelForm, DateTimeInput, TextInput, NumberInput, Form
from django import forms
class CryptoPaymentForm(forms.Form):
    sub_id = forms.IntegerField(required=True)
    wallet_id = forms.IntegerField(required=True)

