from modeltranslation.translator import translator, TranslationOptions
from .models import Offer, Rate, Subscription, Product, SupportTask, Currency


class RateTranslationOptions(TranslationOptions):
    fields = ('name',)

class OfferTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class CurrencyTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Offer, OfferTranslationOptions)
translator.register(Currency, CurrencyTranslationOptions)
translator.register(Product, ProductTranslationOptions)
translator.register(Rate, RateTranslationOptions)
