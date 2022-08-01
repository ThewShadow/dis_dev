import datetime
import service.service as service
from django.shortcuts import redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import View
from main.models import CustomUser
from main.models import Offer
from main.models import Subscription
from main.forms import LoginForm
from main.forms import SubscribeCreateForm
from main.forms import VerifyEmailForm
from main.forms import CustomUserCreationForm
from main.forms import ResetPasswordForm
from main.forms import ResetPasswordVerifyForm
from main.forms import NewPasswordForm, CustomUserSocialCreationForm
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
import logging
from service import crypto
from service import google
import threading
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from main.forms import TransactionForm
import json

logger = logging.getLogger('main')


class SubscriptionCreate(View):

    class_form = SubscribeCreateForm

    def post(self, request, **kwargs):

        selected_offer_id = request.POST.get('offer_id', 0)
        offer = get_object_or_404(Offer, id=selected_offer_id)

        try:
            instance = Subscription.objects.get(
                id=request.session['current_sub_id']
            )
        except (KeyError, Subscription.DoesNotExist):
            instance = None

        form = self.class_form({
                'user': request.user,
                'email': request.POST.get('email'),
                'phone_number': request.POST.get('phone_number'),
                'offer': offer,
                'user_name': request.POST.get('user_name'),
            },
            instance=instance
        )

        if form.is_valid():
            new_subscription = form.save()
            request.session['current_sub_id'] = new_subscription.id
            request.session['current_offer_id'] = selected_offer_id
        else:
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )

        if not instance:
            # this is a new subscription, management must be notified.
            thread = threading.Thread(
                target=new_subscription.notify_managers)
            thread.start()

        return JsonResponse({
                'success': True,
                'sub_id': new_subscription.id,
                'offer_price': offer.price
            },
            status=200
        )


@method_decorator(csrf_exempt, name='dispatch')
class CryptoPayCreate(View):

    def post(self, request, **kwargs):

        type_payment = request.POST.get('currency', None)
        type_blockchain = request.POST.get('blockchain', None)
        offer_id = request.session.get('current_offer_id', None)

        link = crypto.gen_pay_link(type_payment, type_blockchain)
        qrcode_path = crypto.gen_qrcode(link)

        try:
            amount = Offer.objects.get(id=offer_id).price
        except Offer.DoesNotExist:
            amount = None

        logger.debug(f'Crypto payment data: '
                     f'{offer_id} '
                     f'{link} '
                     f'{amount} '
                     f'{qrcode_path}')

        if not offer_id \
                or not link \
                or not amount\
                or not qrcode_path:

            return JsonResponse({
                    'success': False,
                    'message': _('Bad Request')
                },
                status=400
            )
        else:

            if 'Bitcoin' in type_payment:
                currency = 'BTC'
            elif 'Ethereum' in type_payment:
                currency = 'ETH'
            else:
                currency = 'USDT'

            if currency in ['BTC', 'ETH']:
                crypto_amount = crypto.get_amount(currency, amount)
                if crypto_amount == 0:
                    return JsonResponse({
                            'success': False,
                            'message': _('Bad Request')
                        },
                        status=400
                    )
            else:
                crypto_amount = str(amount) + ' ' + currency

            blockchain_name = str(type_blockchain).replace('Blockchain', '')

            return JsonResponse({
                'success': True,
                'payment_link': link,
                'blockchain_name': blockchain_name,
                'amount': crypto_amount,
                'qr': qrcode_path,
                'currency': currency
            })


class GoogleLogin(View):

    def get(self, request, **kwargs):
        url = google.gen_auth_url()
        return HttpResponseRedirect(url)


class GoogleLoginComplete(View):
    class_form = CustomUserSocialCreationForm

    def get(self, request, **kwargs):

        try:
            code = request.GET['code']
        except KeyError:
            logger.warning('The user was unable to register with Google.')
            return redirect(reverse_lazy('index'))

        access_token = google.get_user_auth_token(code)
        if not access_token:
            return redirect(reverse_lazy('index'))

        user_info = google.get_user_info(access_token)
        if not user_info:
            return redirect(reverse_lazy('index'))

        try:
            customer = CustomUser.objects.get(email=user_info['email'])

            if not customer.social_sign_up:
                raise Exception('User is exist')

        except CustomUser.DoesNotExist:
            ref_link = request.COOKIES.get('ref_link', '').lstrip('0')

            form = self.class_form({
                'username': user_info['given_name'],
                'ref_link': ref_link,
                'social_sign_up': True,
                'email': user_info['email'],
                'is_active': True,
                'is_verified': True
            })

            if form.is_valid():
                customer = form.save()
            else:
                customer = None
                logger.warning(f':Social user create error. '
                               f'Form not valid. \n'
                               f'form errors: {form.errors}')
        except:
            return redirect(reverse_lazy('unauthorized'))


        if isinstance(customer, CustomUser):
            login(self.request, customer, backend='main.backends.EmailBackend')

        return redirect(reverse_lazy('profile'))


@method_decorator(csrf_exempt, name='dispatch')
class PayPalPaymentReceiving(View):
    class_form = TransactionForm

    def post(self, request, **kwargs):

        payment_data = json.loads(request.body)

        if 'purchase_units' not in payment_data:
            logger.error('PayPalPaymentReceiving: purchase_units not found')
            return JsonResponse({'success': False}, status=400)

        try:
            data = payment_data['purchase_units'][0]
        except KeyError:
            logger.error('PayPal receiving error. purchase_units not found.')
            return JsonResponse({'success': False}, status=400)
        except IndexError:
            logger.error('PayPal receiving error. purchase_units is empty.')
            return JsonResponse({'success': False}, status=400)

        sub_id = data['custom_id']
        if not sub_id:
            logger.error('PayPalPaymentReceiving: custom_id is empty')
            return JsonResponse({'success': False}, status=400)

        customer_subscription = Subscription.objects.filter(id=sub_id).first()

        form = self.class_form({
            'transaction_id': payment_data['id'],
            'date_create': datetime.datetime.now(),
            'subscription': customer_subscription,
            'pay_type': 'paypal',
        })

        if not form.is_valid():
            logger.error('PayPalPaymentReceiving: form not valid')
            logger.error(dict(form.errors))

            return JsonResponse({'success': False}, status=400)

        transaction = form.save()
        customer_subscription.paid = True
        customer_subscription.save()
        transaction.notify_managers()

        logger.error('PayPalPaymentReceiving: payment receiving success')

        clear_temp_data(request)

        return JsonResponse({'success': True}, status=200)


class CryptoPaymentReceiving(View):
    class_form = TransactionForm

    def post(self, request, **kwargs):

        try:
            customer_subscription = Subscription.objects\
                .filter(id=request.COOKIES.get('sub_id'))\
                .first()
        except Subscription.DoesNotExist:
            return JsonResponse({'success': False}, status=400)

        form = self.class_form({
            'transaction_id': request.POST['proof-hash'],
            'date_create': datetime.datetime.now(),
            'subscription': customer_subscription,
            'pay_type': 'crypto',
            'comment': request.POST['pay_info']
        })

        if form.is_valid():
            form.save()
            clear_temp_data(request)
            return HttpResponse(status=200)
        else:
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )


class Login(View):
    class_form = LoginForm

    def post(self, *args, **kwargs):

        form = self.class_form(self.request.POST)
        if not form.is_valid():
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )

        user = authenticate(
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'])

        if user is None:
            logger.warning(f'Authorized failed: '
                           f'{form.cleaned_data["email"]} '
                           f'{form.cleaned_data["password"]}')

            return JsonResponse({
                    'success': False,
                    'message': _('Wrong login or password')
                },
                status=401
            )

        if not user.is_verified and not user.is_superuser:
            return JsonResponse({
                    'success': False,
                    'message': _('Email not verified')
                },
                status=401
            )

        login(self.request, user=user, backend='main.backends.EmailBackend')

        return JsonResponse({'success': True}, status=200)

    def get(self, request, **kwargs):
        response = redirect('index')
        response.set_cookie(key='show_login', value=True)
        return response


class Registration(View):
    class_form = CustomUserCreationForm

    def post(self, request, **kwargs):
        form = self.class_form(self.request.POST)
        if not form.is_valid():
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )

        try:
            agent_id = int(request.COOKIES.get('ref_link', '').lstrip('0'))
        except ValueError:
            agent_id = None

        new_customer = form.save(commit=False)
        if agent_id:
            new_customer.set_agent(agent_id)
        new_customer.save()

        activation_code = service.gen_verify_code()
        send_code = threading.Thread(
            target=service.send_activation_account_code,
            args=(activation_code, new_customer.email))
        send_code.start()

        request.session['activation_code'] = activation_code
        request.session['activation_email'] = new_customer.email

        return JsonResponse({'success': True}, status=201)


class ResetPasswordConfirm(View):
    class_form = ResetPasswordVerifyForm

    def post(self, request, **kwargs):

        form = self.class_form(request.POST)
        if form.is_valid():
            verify_code = form.cleaned_data.get('verify_code')
            verify_code_check = request.session.get('reset_pass_verify_code')
            if not verify_code_check:
                return JsonResponse({
                        'success': False,
                        'message': _('Session expired')
                    },
                    status=400
                )

            if str(verify_code) == verify_code_check:
                return JsonResponse({'success': True}, status=200)
            else:
                return JsonResponse({
                        'success': False,
                        'message': _('invalid verification code')
                    },
                    status=400
                )
        else:
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )


class ResetPasswordComplete(View):
    class_form = NewPasswordForm

    def post(self, request, **kwargs):

        form = self.class_form(request.POST)
        if form.is_valid():
            reset_pass_email = request.session.get('reset_pass_email')
            if not reset_pass_email:
                return JsonResponse({
                        'success': False,
                        'message': 'Session expired'
                    },
                    status=400
                )

            try:
                user = CustomUser.objects.get(email=reset_pass_email)
            except ObjectDoesNotExist:
                return JsonResponse({
                        'success': False,
                        'message': 'User does not exist'
                    },
                    status=400
                )
            else:
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )


class ResetPassword(View):
    class_form = ResetPasswordForm

    def post(self, request, **kwargs):

        form = self.class_form(request.POST)
        if not form.is_valid():
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )

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
    class_form = VerifyEmailForm

    def post(self, *args, **kwargs):
        form = self.class_form(self.request.POST)
        if not form.is_valid():
            return JsonResponse({
                    'success': False,
                    'message': _('Incorrect input data')
                },
                status=400
            )

        original_code = self.request.session.get('activation_code', None)
        activation_email = self.request.session.get('activation_email', None)
        verifiable_code = form.cleaned_data.get('activation_code')

        if original_code is None or activation_email is None:
            return JsonResponse({
                    'success': False,
                    'message': _('Session expired')
                },
                status=400
            )

        if str(verifiable_code) != str(original_code):
            return JsonResponse({
                    'success': False,
                    'message': _('Incorrect code')
                },
                status=400
            )

        try:
            user = CustomUser.objects.get(email=activation_email)
            user.is_verified = True
            user.is_active = True
            user.save()
        except CustomUser.DoesNotExist:
            return JsonResponse({
                    'success': False,
                    'message': _('User is not found')
                },
                status=400
            )

        login(self.request, user=user, backend='main.backends.EmailBackend')

        return JsonResponse({"success": True})


class PayPalPaymentReturnView(View):

    def get(self, request, **kwargs):
        response = HttpResponseRedirect(reverse_lazy('index'))
        response.set_cookie(key='paid_success', value=True)
        return response


@method_decorator(csrf_exempt, name='dispatch')
class IsAuthenticated(View):

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=401)


def clear_temp_data(request):
    try:
        del request.session['current_sub_id']
    except KeyError:
        pass

    try:
        del request.session['current_offer_id']
    except KeyError:
        pass
