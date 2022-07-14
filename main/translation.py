from modeltranslation.translator import translator, TranslationOptions
from .models import Offer, Rate, Subscription, Product, SupportTask, Currency, Feature, FAQ


class RateTranslationOptions(TranslationOptions):
    fields = ('name',)


class OfferTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class CurrencyTranslationOptions(TranslationOptions):
    fields = ('name',)


class FeatureTranslationOptions(TranslationOptions):
    fields = ('name',)

class FAQTranslationOptions(TranslationOptions):
    fields = ('title', 'answer',)

translator.register(Offer, OfferTranslationOptions)
translator.register(Currency, CurrencyTranslationOptions)
translator.register(Product, ProductTranslationOptions)
translator.register(Rate, RateTranslationOptions)
translator.register(Feature, FeatureTranslationOptions)
translator.register(FAQ, FAQTranslationOptions)
