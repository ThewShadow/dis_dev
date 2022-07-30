from django.contrib import admin
from .models import Product, Rate, Subscription, Offer, Currency, SupportTask, FAQ
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Transaction, Feature


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    readonly_fields = ('id',)
    list_display = (
        'email',
        'is_staff',
        'is_active',
        'username',
        'agent',
        'is_verified',
        'social_sign_up',
    )

    list_filter = ('email', 'is_staff', 'is_active', 'username',)
    fieldsets = (
        (None, {'fields': ('id', 'username', 'email', 'password', 'agent', 'social_sign_up')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_verified', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'id')}
        ),
    )
    filter_horizontal = ('groups', 'user_permissions',)
    search_fields = ('email',)
    ordering = ('email',)


class RateAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('count', 'name',)}


class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('order_date',)
    list_display = ('user', 'offer', 'phone_number', 'order_date', 'paid', 'is_active')
    list_filter = ('user', 'offer', 'phone_number', 'order_date', 'paid', 'is_active')
    search_fields = ('phone_number',)

class OfferAdmin(TranslationAdmin):
    filter_horizontal = ['features']
    list_display = ('name', 'product', 'rate', 'price',)
    list_filter = ('name', 'product', 'rate', 'price',)
    search_fields = ('name', 'product__name', 'user__username')

class CurrencyAdmin(TranslationAdmin):
    pass


class ProductAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}

class FeatureAdmin(TranslationAdmin):
    pass

class FAQAdmin(TranslationAdmin):
    pass

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'pay_type', 'date_create', 'subscription')
    list_filter = ('transaction_id', 'pay_type', 'date_create', 'subscription')
    search_fields = ('transaction_id', 'pay_type', 'subscription')



admin.site.register(Rate, RateAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(SupportTask)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Feature, FeatureAdmin)
