from main import models
from config import settings
from django.utils import translation
from django import shortcuts
from django import urls


def get_payment_form(request):
    test_url = settings.NGROK_DOMAIN

    sub_id = request.POST.get('sub_id', None)
    lang = translation.get_language().upper()
    sub_obj = shortcuts.get_object_or_404(models.Subscription, id=sub_id)

    if settings.DEBUG and settings.NGROK_DOMAIN:
        # notify_url = request.build_absolute_uri(urls.reverse_lazy('paypal-ipn')).replace('localhost', '127.0.0.1'),
        # return_url = request.build_absolute_uri(urls.reverse_lazy('paypal_return')).replace('localhost', '127.0.0.1'),
        # cancel_return = request.build_absolute_uri(urls.reverse_lazy('paypal_cancel')).replace('localhost', '127.0.0.1'),

        notify_url = test_url + urls.reverse_lazy('paypal-ipn'),
        return_url = test_url + urls.reverse_lazy('paypal_return'),
        cancel_return = test_url + urls.reverse_lazy('paypal_cancel'),
    else:
        notify_url = request.build_absolute_uri(urls.reverse_lazy('paypal-ipn')),
        return_url = request.build_absolute_uri(urls.reverse_lazy('paypal_return')),
        from urllib import parse

        cancel_return = request.build_absolute_uri(urls.reverse_lazy('paypal_cancel')),

        cancel_return = parse.urlencode(cancel_return)
    return {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": sub_obj.offer.price,
        "currency_code": str(sub_obj.offer.currency.code).upper(),
        "item_name": 'test',
        "invoice": str(sub_id),
        "notify_url": notify_url,
        "return_url": return_url,
        "cancel_return": cancel_return,
        "lc": lang,
        "no_shipping": '1',
    }