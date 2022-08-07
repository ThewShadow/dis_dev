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
from .models import FAQ
from .forms import SupportTaskCreateForm
from .forms import ChangeUserInfoForm
from .forms import ChangeSubscibeStatusForm
from .forms import SubscribeCreateForm
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
import logging
from config import settings
from django.core.paginator import Paginator


logger = logging.getLogger('main')

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


class LogoutView(View):

    def post(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))

    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))


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


class ManagerPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'main/management.html'

    show_pages_default = 5
    page_number_default = 1

    def get(self, request, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()

        response = super().get(request, **kwargs)

        current_page = self.request.GET.get('page')
        show_pages = self.request.GET.get('show_pages')

        if current_page:
            response.set_cookie(key='current_page', value=current_page)

        if show_pages:
            response.set_cookie(key='show_pages', value=show_pages)

        return response

    def post(self, request, **kwargs):
        form = ChangeSubscibeStatusForm(request.POST)
        if form.is_valid():
            subscr_obj = get_object_or_404(
                Subscription,
                id=form.cleaned_data['sub_id'])

            subscr_obj.is_active = True
            subscr_obj.save()
            subscr_obj.notify_customer()

        return redirect(reverse_lazy('manager_panel'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        show_pages = self.request.GET.get('show_pages')
        if not show_pages:
            show_pages = self.request.COOKIES.get(
                'show_pages',
                self.show_pages_default)

        page_number = self.request.GET.get('page')
        if not page_number:
            page_number = self.request.COOKIES.get(
                'current_page',
                self.page_number_default)

        search = self.request.GET.get('search')
        related_fields = ['offer', 'user', 'offer__product', 'offer__rate', 'offer__currency']
        if search:
            from django.db.models import Q
            new_subs = Subscription.objects.filter(
                Q(offer__name__contains=search)
                | Q(phone_number__contains=search)
                | Q(offer__product__name__contains=search)
                | Q(email__contains=search)
            ).order_by('-order_date').select_related(*related_fields)
        else:
            new_subs = Subscription.objects.order_by('-order_date').select_related(*related_fields)

        pag = Paginator(new_subs, show_pages)
        try:
            page = pag.page(page_number)
        except django.core.paginator.EmptyPage:
            page = pag.page(self.page_number_default)
            page_number = self.page_number_default

        context['page_range'] = pag.page_range
        context['current_page'] = int(page_number)
        context['new_subscriptions'] = page
        context['show_pages'] = show_pages
        context['num_count'] = pag.count
        context['start_index'] = page.start_index()
        context['end_index'] = page.end_index()

        try:
            context['next_page'] = page.next_page_number()
        except:
            pass

        try:
            context['previous_page'] = page.previous_page_number()
        except:
            pass

        return context


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

        return render(
            request,
            'main/pay_crypto_wallet.html',
            context={'offer_descr': offer_descr})



