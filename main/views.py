import django.core.paginator
from django.shortcuts import redirect, get_object_or_404, HttpResponse, render
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, CreateView, TemplateView, View
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


logger = logging.getLogger('main')


class ReportView(ContextMixin, View):
    paginate_by = 10
    model = None
    template_name = f'main/report_{model}.html'

    def get(self, request):
        queryset = self.get_queryset()
        show = self.define_number_to_show(len(queryset))
        page_number = self.get_page_number()
        if not show:
            show = self.paginate_by

        page_obj = self.paginate(queryset, show, page_number)

        context = self.get_context_data()
        if page_obj:
            context['count_obj'] = queryset.count() if not isinstance(queryset, list) else len(queryset)
            context['page_obj'] = page_obj
            context['show_pages'] = show
            context['current_page'] = page_number
            context['pages_count'] = range(1, page_obj.paginator.num_pages + 1)
            context['query_string'] = request.GET.get('q', '')
            context['start_objects'] = (show * page_obj.number + 1) - show
            context['end_objects'] = (show * page_obj.number - show) + len(page_obj.object_list)
        else:
            context['count_obj'] = 0
            context['page_obj'] = None
            context['show_pages'] = request.GET.get('q', '')
            context['current_page'] = 1
            context['pages_count'] = range(1,2)
            context['query_string'] = request.GET.get('q', '')
            context['start_objects'] = 0
            context['end_objects'] = 0

        response = render(request, self.template_name, context)

        response.set_cookie(key='current_page', value=page_number)
        response.set_cookie(key='show', value=show)

        return response

    def define_number_to_show(self, list_count):
        show = self.paginate_by
        if self.request.GET.get('show'):
            show = self.request.GET.get('show')
        elif self.request.COOKIES.get('show'):
            show = self.request.COOKIES.get('show')

        if not isinstance(show, int):
            try:
                show = int(show)
            except ValueError:
                show = self.paginate_by
        if show > list_count:
            show = list_count
        return show

    def get_page_number(self):
        page_number = self.request.GET.get('page')
        if page_number:
            return page_number
        else:
            return self.request.COOKIES.get('current_page', 1)

    def paginate(self, queryset, show_elements, page_number):
        if not queryset:
            return []
        else:
            return Paginator(queryset, show_elements).get_page(page_number)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()

        return context

from django.views.generic import RedirectView
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


class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'main/user_profile.html'
    login_url = 'unauthorized'
    redirect_field_name = 'redirect_to'
    form_class = ChangeUserInfoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        user_data = CustomUser.objects.select_related('agent').get(id=self.request.user.id)

        context['user_id'] = user_data.id
        context['questions_list'] = FAQ.objects.all()
        context['agent'] = user_data.agent.username
        context['user_subscriptions'] = Subscription.objects.filter(
            user__id=user_data.id).prefetch_related(
                'offer__product',
                'offer__rate'
            )
        context['form'] = ChangeUserInfoForm(initial={
            'email': user_data.email,
            'username': user_data.username
        })

        context['referrals'] = self.request.user.referrals.prefetch_related('subscriptions_list').all()
        context['all_users'] = CustomUser.objects.all().count()

        agents = list(CustomUser.objects.all().values('agent__id'))
        agents_ids = map(lambda el: el['agent__id'], agents)
        context['all_agents'] = len(set(agents_ids))
        return context

    def post(self, *args, **kwargs):
        form = ChangeUserInfoForm(self.request.POST)
        if form.is_valid():
            service.change_profile_info(self.request, form)

        return super().post(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('profile')


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


class ManagerPanelView(ReportView):
    model = Subscription
    template_name = 'reports/report_subscriptions.html'

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
        return redirect(reverse_lazy('manager_panel'))

    def get_queryset(self):
        objects_list = Subscription.objects.filter().order_by('-order_date')
        query = self.request.GET.get('q', '').strip()
        if query:
            objects_list = objects_list.filter(
                Q(offer__name__contains=query) | Q(phone_number__contains=query)
                | Q(offer__product__name__contains=query) | Q(email__contains=query)
            )
        objects_list = objects_list.select_related('offer', 'user', 'offer__product', 'offer__rate', 'offer__currency')
        return objects_list


class Unauthorized(TemplateView):
    template_name = 'main/unauthorized.html'


class PayPalErrorView(TemplateView):
    template_name = 'main/paypal_error.html'


class CryptoPayment(View):

    def get(self, request, **kwargs):
        try:
            current_sub_id = request.session['current_sub_id']
        except KeyError:
            raise Http404

        subscription = get_object_or_404(
            Subscription,
            id=current_sub_id)

        offer_descr = str(subscription.offer)
        context = {}
        context['currencies'] = Currency.objects.filter(crypto=True)
        context['wallets'] = CryptoWallet.objects.all()
        context['offer_descr'] = offer_descr
        return render(request,'main/pay_crypto_wallet.html', context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currencies'] = Currency.objects.filter(crypto=True)
        context['wallets'] = CryptoWallet.objects.all()
        return context


class ReferralsReportView(LoginRequiredMixin, ReportView):
    model = CustomUser
    template_name = 'reports/report_referrals.html'

    def get_queryset(self):
        user_list = self.model.objects.filter(agent__id=self.request.user.id).order_by('-date_joined')
        query = self.request.GET.get('q', '').strip()
        if query is not None:
            user_list = user_list.filter(Q(email__contains=query) | Q(username__contains=query))
        return user_list


class ReportAgentsView(LoginRequiredMixin, ReportView):
    template_name = 'reports/report_agents.html'
    model = CustomUser

    def get_queryset(self, *args):
        objects_list = self.model.objects.annotate(order=Count('referrals')).filter(order__gt=0).select_related('agent').order_by('-order')
        query = self.request.GET.get('q', '').strip()
        if query:
            return objects_list.filter(Q(agent__email__contains=query) | Q(agent__username__contains=query))

        return objects_list

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['referrals_count'] = self.model.objects.filter(is_active=True, is_agent=False).count()
        context['agents_count'] = self.model.objects.annotate(order=Count('referrals')).filter(order__gt=0).count()
        return context


class MySubscriptionsView(LoginRequiredMixin, TemplateView):
    template_name = 'main/my_subsctiptions.html'

    def get_context_data(self, *args, **kwargs):
       context = super().get_context_data(*args, **kwargs)
       context['user_subscriptions'] = Subscription.objects.filter(
           user__id=self.request.user.id).prefetch_related(
           'offer__product',
           'offer__rate'
       )
       return context



class AccountInfoView(LoginRequiredMixin, View):
    template_name = 'main/my_info.html'
    form_class = ChangeUserInfoForm

    def dispatch(self, request, *args, **kwargs):
        if request.POST:
            form = self.form_class(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
        else:
            form = self.form_class(model_to_dict(request.user))

        context = self.get_context_data()
        context.update({'form': form})
        return render(request, template_name=self.template_name, context=context)

    def get_context_data(self, *args, **kwargs):
        context = {}
        context['user_id'] = self.request.user.id
        return context