from django.urls import path, include
from main import views
from django.contrib import admin

from main.views import ReportAgentsView, ReferralsReportView, AccountInfoView, MySubscriptionsView


urlpatterns = [

    # main views
    path('', views.IndexView.as_view(),
         name='index'),
    # path('profile/info', views.ProfileView.as_view(),

    path('profile/mysubscriptions/', MySubscriptionsView.as_view(),
        name='my_sub_list'),
    path('profile/account_info/', AccountInfoView.as_view(),
        name='my_info'),
    path('accounts/logout/', views.LogoutView.as_view(),
         name='logout'),
    path('offers/<slug:slug>/<slug:rate_slug>/', views.OffersView.as_view(),
         name='offers'),
    path('offers/<slug:slug>/', views.OffersView.as_view(),
         name='offers_redirect'),
    path('unauthorized/', views.Unauthorized.as_view(),
         name='unauthorized'),

    path('faq/', views.FAQView.as_view(),
         name='faq_list'),

    path('admin_panel/', views.ManagerPanelView.as_view(),
         name='manager_panel'),

    path('paypal_error/', views.PayPalErrorView.as_view(),
         name='paypal_error'),
    path('crypto_payment/', views.CryptoPayment.as_view(),
         name='crypto-pay'),
    path('reports/agents/', ReportAgentsView.as_view(), name='report-agents'),

    path('reports/referrals', ReferralsReportView.as_view(), name='report-referrals'),
]
