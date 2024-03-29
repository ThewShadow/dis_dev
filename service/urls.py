from django.urls import path, include
from . import views
from .views import CryptoWallets

app_name = 'service'

urlpatterns = [
    path('accounts/login/', views.Login.as_view(),
         name='login'),
    path('accounts/register/', views.Registration.as_view(),
         name='registration'),
    path('accounts/activation_email/', views.ActivationEmail.as_view(),
         name='activation_email'),
    path('accounts/reset_password/start/', views.ResetPassword.as_view(),
         name='reset_pass'),
    path('accounts/reset_password/confirm/', views.ResetPasswordConfirm.as_view(),
         name='reset_pass_confirm'),
    path('accounts/reset_password/complete/', views.ResetPasswordComplete.as_view(),
         name='reset_pass_complete'),
    path('social/google_oauth2/login_complete/', views.GoogleLoginComplete.as_view(),
         name='google-auth2-complete'),
    path('social/google_oauth2/login/', views.GoogleLogin.as_view(),
         name='google-auth2'),
    path('payments/crypto/create/', views.CryptoPayCreate.as_view(),
         name='crypto-pay-create'),
    path('subscriptions/create/', views.SubscriptionCreate.as_view(),
         name='create_subscription'),
    path('paypal/receiving_payment/', views.PayPalPaymentReceiving.as_view(),
         name='paypal_form_create'),

    path('is_authenticated/', views.IsAuthenticated.as_view(),
         name='check-login'),

    # paypal payment callbacks
    path('paypal_return/', views.PayPalPaymentReturnView.as_view(),
         name='paypal_return'),

    path('crypto_payment_confirm/', views.CryptoPaymentReceiving.as_view(),
         name='crypto-pay-confirm'),
    path('create_support_task/', views.SupportTaskCreateView.as_view()),
    path('blockchains/list/', CryptoWallets.as_view())

]


