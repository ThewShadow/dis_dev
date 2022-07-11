from django.urls import path, include
from main import views


urlpatterns = [

    # main views
    path('', views.IndexView.as_view(),
         name='index'),
    path('profile/info', views.ProfileView.as_view(),
         name='profile'),
    path('profile/subscriptions/', views.UserSubscriptionsView.as_view(),
         name='user_subscriptions'),
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

]
