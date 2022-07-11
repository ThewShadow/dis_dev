import datetime
import service.service as service
from django.shortcuts import redirect, get_object_or_404, render, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View
from main.models import CustomUser
from main.models import Offer
from main.models import Subscription, Transaction
from main.forms import LoginForm
from main.forms import SubscribeCreateForm
from main.forms import VerifyEmailForm
from main.forms import CustomUserCreationForm
from main.forms import ResetPasswordForm
from main.forms import ResetPasswordVerifyForm
from main.forms import NewPasswordForm
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
import logging
from service import crypto
from service import google
import threading
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


logger = logging.Logger(__name__)


class SubscriptionCreate(View):

    def post(self, request, **kwargs):

        form = SubscribeCreateForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse({'success': False,
                                 'error_messages': dict(form.errors)},
                                status=400)

        offer = get_object_or_404(Offer, id=form.cleaned_data['offer_id'])

        new_subscription = None
        try:
            new_subscription = Subscription.objects.get(
                offer__id=offer.id,
                user=self.request.user,
                email=form.cleaned_data['email'],
                paid=False)
        except:
            new_subscription = Subscription()
            new_subscription.email = form.cleaned_data['email']
            new_subscription.phone_number = form.cleaned_data['phone_number']
            new_subscription.offer = offer
            new_subscription.user_name = form.cleaned_data['user_name']
            new_subscription.user = self.request.user

            try:
                new_subscription.save()

                thread = threading.Thread(target=new_subscription.notify_managers)
                thread.start()

            except Exception as excp:
                logger.critical(excp)

        finally:
            if not new_subscription:
                return JsonResponse({'success': False}, status=400)

            resp = {'success': True, 'sub_id': new_subscription.id, 'offer_price': offer.price}
            request.session['current_offer_id'] = form.cleaned_data['offer_id']
            return JsonResponse(resp, status=200)


class CryptoPayCreate(View):

    def post(self, request, **kwargs):
        type_payment = request.POST.get('type-payment')
        type_blockchain = request.POST.get('type-blockchain')

        if type_payment and type_blockchain:
            link = crypto.gen_crypto_pay_link(type_payment, type_blockchain)

            offer_id = request.session.get('current_offer_id')
            amount = Offer.objects.get(id=offer_id).price

            curr = None
            if 'Bitcoin' in type_payment:
                curr = 'BTC'
            elif 'Ethereum' in type_payment:
                curr = 'ETH'

            if curr:
                crypto_amount = crypto.get_crypto_amount(curr, amount)
            else:
                crypto_amount = amount + ' USDT'

            response = {
                'success': True,
                'payment_link': link,
                'blockchain_name': str(type_blockchain).replace('Blockchain', ''),
                'amount': crypto_amount
            }

            return JsonResponse(response)
        else:
            return JsonResponse({'success': False,
                                 'message': _('Bad Request')},
                                status=400)


class GoogleLogin(View):

    def get(self, request, **kwargs):
        url = google.gen_auth_url()
        return HttpResponseRedirect(url)


class GoogleLoginComplete(View):

    def get(self, request, **kwargs):
        code = request.GET.get('code')
        if not code:
            return redirect(reverse_lazy('index'))

        access_token = google.get_user_auth_token(code)

        user_info = google.get_user_info(access_token)

        try:
            user = CustomUser.objects.get(email=user_info['email'])
        except ObjectDoesNotExist:
            user = CustomUser()
            user.email = user_info['email']
            user.username = user_info['given_name']
            user.save()
        finally:
            login(self.request, user, backend='main.backends.EmailBackend')

        return redirect(reverse_lazy('profile'))


@method_decorator(csrf_exempt, name='dispatch')
class PayPalPaymentReceiving(View):

    def post(self, request, **kwargs):
        from main.forms import TransactionForm
        import json
        payment_data = json.loads(request.body)

        if 'purchase_units' not in payment_data:
            return JsonResponse({'success': False}, status=400)

        for data in payment_data['purchase_units']:
            sub_id = data['custom_id']
            if not sub_id:
                return JsonResponse({'success': False}, status=400)

            customer_subscription = Subscription.objects.filter(id=sub_id).first()

            init = {
                'transaction_id': payment_data['id'],
                'date_create': datetime.datetime.now(),
                'subscription': customer_subscription
            }

            form = TransactionForm(init)

            if form.is_valid():
                transaction = form.save()
                transaction.notify_managers()

                customer_subscription.paid = True
                customer_subscription.save()

                return JsonResponse({'success': True}, status=200)
            else:
                return JsonResponse({'success': False}, status=400)


class Login(View):

    def post(self, *args, **kwargs):

        form = LoginForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse({'success': False,
                                 'error_messages': dict(form.errors)},
                                status=400)

        user = authenticate(
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'])

        if user is None:
            return JsonResponse({'success': False,
                                 'message': _('Wrong login or password')},
                                status=401)

        if not user.verified and not user.is_superuser:
            return JsonResponse({'success': False,
                                 'message': _('Email not verified')},
                                status=401)

        login(self.request, user)

        return JsonResponse({'success': True}, status=200)


class Registration(View):
    class_form = CustomUserCreationForm

    def post(self, request, **kwargs):

        form = self.class_form(self.request.POST)
        if not form.is_valid():
            return JsonResponse({'success': False,
                                'error_messages': dict(form.errors)},
                                status=400)

        customer_email = form.cleaned_data['email']
        activation_code = service.gen_verify_code()

        send_code = threading.Thread(
            target=service.send_activation_account_code,
            args=(activation_code, customer_email))
        send_code.start()

        request.session['activation_code'] = activation_code
        request.session['activation_email'] = customer_email

        form.save()

        return JsonResponse({'success': True}, status=201)


class ResetPasswordConfirm(View):

    def post(self, request, **kwargs):

        form = ResetPasswordVerifyForm(request.POST)
        if form.is_valid():
            verify_code = form.cleaned_data.get('verify_code')

            verify_code_check = request.session.get('reset_pass_verify_code')
            if not verify_code_check:
                return JsonResponse(
                    {'success': False, 'message': _('Session expired')}, status=400)

            if str(verify_code) == verify_code_check:
                return JsonResponse({'success': True}, status=200)
            else:
                return JsonResponse({'success': False,
                                     'message': _('invalid verification code')},
                                    status=400)
        else:
            return JsonResponse({'success': False,
                                 'error_messages': dict(form.errors)},
                                status=400)


class ResetPasswordComplete(View):

    def post(self, request, **kwargs):

        form = NewPasswordForm(request.POST)
        if form.is_valid():
            reset_pass_email = request.session.get('reset_pass_email')
            if not reset_pass_email:
                return JsonResponse({'success': False,
                                     'message': 'Session expired'},
                                    status=400)

            try:
                user = CustomUser.objects.get(email=reset_pass_email)
            except ObjectDoesNotExist:
                return JsonResponse({'success': False,
                                     'message': 'User does not exist'},
                                    status=400)
            else:
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False,
                                 'error_messages': dict(form.errors)},
                                status=400)


class ResetPassword(View):

    def post(self, request, **kwargs):

        form = ResetPasswordForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'success': False,
                                 'error_messages': dict(form.errors)},
                                status=400)

        customer_email = form.cleaned_data['email']
        reset_code = service.gen_verify_code()

        request.session['reset_pass_email'] = customer_email
        request.session['reset_pass_verify_code'] = reset_code

        send_reset_code = threading.Thread(
            target=service.send_reset_password_code,
            args=(reset_code, customer_email))
        send_reset_code.start()

        return JsonResponse({'success': True}, status=200)


class ActivationEmail(View):

    def post(self, *args, **kwargs):
        form = VerifyEmailForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse({"success": False,
                                 'message': _('Incorrect input data')},
                                status=400)

        original_code = self.request.session.get('activation_code', None)
        activation_email = self.request.session.get('activation_email', None)
        verifiable_code = form.cleaned_data.get('activation_code')

        if original_code is None or activation_email is None:
            return JsonResponse({"success": False,
                                 'message': _('Session expired')},
                                status=400)

        if str(verifiable_code) != str(original_code):
            return JsonResponse({"success": False,
                                 'message': _('Incorrect code')},
                                status=400)

        try:
            user = CustomUser.objects.get(email=activation_email)
            user.verified = True
            user.save()
        except ObjectDoesNotExist:
            return JsonResponse({"success": False,
                                 'message': _('User is not found')},
                                status=400)

        return JsonResponse({"success": True})




class PayPalPaymentReturnView(View):

    def get(self, request, **kwargs):
        response = HttpResponseRedirect(reverse_lazy('index'))
        response.set_cookie(key='paid_success', value=True)
        return response








