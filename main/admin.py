from django.contrib import admin
from .models import Product, Rate, Subscription, Offer, Currency, SupportTask, PaymentType, FAQ
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Transaction

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active', 'username',)
    list_filter = ('email', 'is_staff', 'is_active', 'username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class RateAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('count', 'name',)}

class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('order_date',)

class OfferAdmin(TranslationAdmin):
    pass

class CurrencyAdmin(TranslationAdmin):
    pass


class ProductAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}



admin.site.register(Rate, RateAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(SupportTask)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(PaymentType)
admin.site.register(FAQ)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Transaction)


