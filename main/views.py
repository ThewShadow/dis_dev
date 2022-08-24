import django.core.paginator
from django.shortcuts import redirect, get_object_or_404, HttpResponse, render
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, CreateView, TemplateView, View
from django.views.generic.edit import ProcessFormView
from datetime import datetime
from service import service
from django.core.exceptions import PermissionDenied
from .models import CustomUser
from .models import Offer
from .models import Subscription
from .models import Product
from .models import FAQ, CryptoWallet, Currency
from .forms import SupportTaskCreateForm
from .forms import ChangeUserInfoForm
from .forms import ChangeSubscibeStatusForm
from .forms import SubscribeCreateForm
from django.views.generic.detail import ContextMixin
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
import logging
from config import settings
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.base import ContextMixin, View
from django.forms.models import model_to_dict
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.translation import gettext
from django.views.generic import RedirectView

logger = logging.getLogger('main')


class CookiePaginationMixin:

    def get_paginate_by(self, queryset):
        list_count = queryset.count()
        paginate_by = self.request.GET.get('show') \
                      or self.request.COOKIES.get('show')
        try:
            return int(paginate_by)
        except TypeError:
            return super().get_paginate_by(queryset)


class IndexView(ListView):
    template_name = 'main/index.html'
    model = Product

    def get(self, request):
        ref_id = request.GET.get('ref')
        response = super().get(self, request)
        if ref_id:
            response = redirect(reverse_lazy('index'))
            response.set_cookie(key='ref_link', value=ref_id.strip())
            logger.info(f'Save refer id {ref_id}')
        return response



class LogoutView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        logout(self.request)
        return response


class OffersView(ListView):
    template_name = 'main/offers.html'
    model = Offer

    def get(self, *args, **kwargs):
        rate_slug = self.kwargs.get('rate_slug', None)
        if not rate_slug:
            product_slug = self.kwargs.get('slug', None)

            offers = Offer.objects.filter(product__slug=product_slug)
            if offers.exists():
                min_offer = offers.order_by('price')
                min_offer = min_offer.first()
                rate_slug = min_offer.rate.slug

            if rate_slug:
                kwargs['slug'] = product_slug
                kwargs['rate_slug'] = rate_slug
                return redirect(reverse_lazy('offers', kwargs=kwargs))

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        form = SubscribeCreateForm(self.request.POST)
        if form.is_valid():
            new_subscription = Subscription.objects.create(form)
            new_subscription.save()

            resp = {'sub_id': new_subscription.id}
            return HttpResponse(resp, status=200)
        else:
            return HttpResponse({'error': True}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('slug')

        context['product'] = get_object_or_404(Product, slug=product_id)
        context['sub_create_form'] = SubscribeCreateForm()

        offers_related_field = ['rate']

        rate_slug = self.kwargs.get('rate_slug', None)
        if not rate_slug:
            context['offers'] = Offer.objects.filter(product__slug=product_id).select_related(*offers_related_field)
        else:
            context['rate_slug'] = rate_slug
            context['offers'] = Offer.objects.filter(
                product__slug=product_id,
                rate__slug=rate_slug).order_by('price').select_related(*offers_related_field)
            rates = []
            for offer in Offer.objects.filter(product__slug=product_id).order_by('price').select_related(*offers_related_field):
                if offer.rate not in rates:
                    rates.append(offer.rate)
            context['rates'] = rates

        return context


class UserSubscriptionsView(LoginRequiredMixin, ListView):
    login_url = 'unauthorized'
    redirect_field_name = 'redirect_to'
    model = Subscription
    form_class = ChangeUserInfoForm
    template_name = 'main/user_subscriptions.html'

    def get_context_data(self, *args, **kwargs):
        context= super().get_context_data()
        context['user_subscriptions'] = Subscription.objects.filter(
            user__id=self.request.user.id)
        return context

class AboutUsView(TemplateView):
    template_name = 'main/about_us.html'


class FAQView(ListView):
    model = FAQ
    template_name = 'main/faq.html'
    context_object_name = 'questions_list'


class PaidCompleteView(View):

    def get(self, request, **kwargs):
        response = redirect('index')
        response.set_cookie(key='paid_success', value=True)
        return response


class ManagerPanelView(LoginRequiredMixin, CookiePaginationMixin, ListView):
    model = Subscription
    template_name = 'reports/report_subscriptions.html'
    paginate_by = 10

    def get(self, request, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()

        response = super().get(request, **kwargs)
        return response

    def post(self, request, **kwargs):
        form = ChangeSubscibeStatusForm(request.POST)
        if form.is_valid():
            subscr_obj = get_object_or_404(self.model, id=form.cleaned_data['sub_id'])
            subscr_obj.is_active = True
            subscr_obj.save()
            subscr_obj.notify_customer()
        return redirect(self.te)

    def get_queryset(self):
        objects_list = Subscription.objects.filter().order_by('-order_date')
        query = self.request.GET.get('q', '').strip()
        if query:
            objects_list = objects_list.filter(
                Q(offer__name__contains=query) | Q(phone_number__contains=query)
                | Q(offer__product__name__contains=query) | Q(email__contains=query)
            )
        objects_list = objects_list.select_related(
            'offer', 'user', 'offer__product', 'offer__rate', 'offer__currency'
        )
        return objects_list


class Unauthorized(TemplateView):
    template_name = 'main/unauthorized.html'


class PayPalErrorView(TemplateView):
    template_name = 'main/paypal_error.html'


class CryptoPayment(TemplateView):
    template_name = 'main/pay_crypto_wallet.html'

    def get_context_data(self, **kwargs):
        current_sub_id = self.request.session.get('current_sub_id', 0)
        subscription = get_object_or_404(Subscription, id=current_sub_id)

        context = super().get_context_data(**kwargs)
        context.update({
            'currencies': Currency.objects.filter(crypto=True),
            'wallets': CryptoWallet.objects.all()
        })
        return context


class ReferralsReportView(LoginRequiredMixin, CookiePaginationMixin, ListView):
    template_name = 'reports/report_referrals.html'
    model = CustomUser
    paginate_by = 2

    def get_queryset(self):
        objects_list = self.model.objects.filter(agent__id=self.request.user.id)
        query = self.request.GET.get('q', '').strip()
        if query:
            objects_list = objects_list.filter(
                Q(email__contains=query) | Q(username__contains=query)
            )
        return objects_list

    def get_ordering(self):
        retur('-date_joined', )


class ReportAgentsView(LoginRequiredMixin, CookiePaginationMixin, ListView):
    template_name = 'reports/report_agents.html'
    model = CustomUser
    paginate_by = 2

    def get_queryset(self, *args):
        objects_list = self.model.objects.annotate(order=Count('referrals'))\
            .filter(order__gt=0).select_related('agent')

        query = self.request.GET.get('q', '').strip()
        if query:
            objects_list = objects_list.filter(
                Q(email__contains=query) | Q(username__contains=query)
            )
        return objects_list

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'referrals_count': self.model.objects.filter(is_active=True, is_agent=False).count(),
            'agents_count': self.model.objects.annotate(order=Count('referrals')).filter(order__gt=0).count()
        })
        return context

    def get_ordering(self):
        retur('-order', )

class MySubscriptionsView(LoginRequiredMixin, ListView):
    template_name = 'main/my_subsctiptions.html'
    context_object_name = 'user_subscriptions'
    model = Subscription
    paginate_by = 10

    def get_queryset(self):
        self.queryset = self.model.objects.filter(user__id=self.request.user.id)\
            .prefetch_related('offer__product', 'offer__rate')
        return super().get_queryset()

    def get_ordering(self):
        return ('-order_date',)


class AccountInfoView(LoginRequiredMixin, View):
    template_name = 'main/my_info.html'
    form_class = ChangeUserInfoForm

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'POST':
            form = self.form_class(request.POST, instance=user)
            if form.is_valid():
                form.save()
        else:
            initial = model_to_dict(user)
            form = self.form_class(initial=initial)

        context = {
            'form': form
        }

        return render(
            request=request,
            template_name=self.template_name,
            context=context
        )