import datetime
from django.core.mail import EmailMessage
from django.db.models import F
from service.forms import CryptoPaymentForm
from service.service import gen_verify_code
from django.shortcuts import redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import View, FormView
from service.crypto import CryptoPaymentGenerator
from config import settings
from main.forms import LoginForm, SupportTaskCreateForm, ChangePasswordForm
from main.forms import SubscribeCreateForm
from main.forms import VerifyEmailForm
from main.forms import CustomUserCreationForm
from main.forms import ResetPasswordForm
from main.forms import ResetPasswordVerifyForm
from main.forms import CustomUserSocialCreationForm
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext as _
from service import google
import threading
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from main.forms import TransactionForm
import json
from main.notifications import *

logger = logging.getLogger('main')


class SubscriptionCreate(View):

    class_form = SubscribeCreateForm

    def post(self, request, **kwargs):

        selected_offer_id = request.POST.get('offer_id', 0)
        offer = get_object_or_404(Offer, id=selected_offer_id)

        form = self.class_form({
                'user': request.user,
                'email': request.POST.get('email'),
                'phone_number': request.POST.get('phone_number'),
                'offer': offer,
                'user_name': request.POST.get('user_name'),
                'service_password': request.POST.get('service_password'),
                'is_exist_account': request.POST.get('is_exist_account'),
                'communication_preferences': request.POST.get('communication_preferences')
            },
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

        SubscriptionCreateMessage(new_subscription).inform()

        return JsonResponse({
                'success': True,
                'sub_id': new_subscription.id,
                'offer_price': offer.price
            },
            status=200
        )


@method_decorator(csrf_exempt, name='dispatch')
class CryptoPayCreate(View):
    def post(self, request):
        payment_query = {
            'sub_id': request.session.get('current_sub_id'),
            'wallet_id': request.POST.get('wallet_id'),
        }
        form = CryptoPaymentForm(payment_query)
        if not form.is_valid():
            return JsonResponse({'success': False}, status=400)
        else:
            cpg = CryptoPaymentGenerator(
                sub_id=form.cleaned_data.get('sub_id'),
                wallet_id=form.cleaned_data.get('wallet_id'),
            )
            try:
                payment_data = cpg.get_payment_details()
            except Exception as e:
                logger.critical(f'Generate crypto payment error \n error: {e}')
                return JsonResponse({'success': False}, status=400)

            return JsonResponse(
                {
                    'success': True,
                    'payment_data': payment_data
                }
            )


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
                'email_verified': True
            })

            if form.is_valid():
                customer = form.save()
            else:
                customer = None
                logger.warning(f':Social user create error. '
                               f'Form not valid. \n'
                               f'form errors: {form.errors}')
        except Exception:
            # the user is already registered through the basic registration
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
        # transaction.notify_managers()
        SubscriptionPaymentMessage(transaction).inform()

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

        if not user.email_verified and not user.is_superuser:
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
            return JsonResponse({'success': False,
                                 'error_messages': dict(form.errors)},
                                status=400)

        activation_code = gen_verify_code()

        EmailActivationCodeMessage(form.cleaned_data['email'], activation_code).inform()

        try:
            agent_id = int(request.COOKIES.get('ref_link', '').lstrip('0'))
        except ValueError:
            agent_id = None

        new_customer = form.save(commit=False)
        if agent_id:
            new_customer.set_agent(agent_id)
        new_customer.save()

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
                request.session['allow_reset_pass'] = True
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
    class_form = ChangePasswordForm

    def post(self, request, **kwargs):
        if not request.session.get('allow_reset_pass', False):
            return JsonResponse({'success': False}, status=403)

        user = self.get_user()
        if user is None:
            logger.warning('Reset password fail. incorrect reset_pass_email')
            return JsonResponse({'success': False, 'message': 'Session expired'}, status=400)

        form = self.class_form(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            del request.session['allow_reset_pass']
            login(request, user, backend='main.backends.EmailBackend')
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)

    def get_user(self):
        reset_pass_email = self.request.session.get('reset_pass_email')
        try:
            return CustomUser.objects.get(email=reset_pass_email)
        except CustomUser.DoesNotExist:
            return None


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
        reset_code = gen_verify_code()

        request.session['reset_pass_email'] = customer_email
        request.session['reset_pass_verify_code'] = reset_code

        ResetPasswordCodeMessage(customer_email, reset_code).inform()

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
            user.email_verified = True
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


class SupportTaskCreateView(View):
    form_class = SupportTaskCreateForm

    def post(self, request, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            support_task = form.save()

            title = f'Customer appeal from {support_task.email}'
            msg = EmailMessage(
                title,
                support_task.description,
                settings.DEFAULT_FROM_EMAIL,
                to=settings.MANAGERS_EMAILS
            )
            if support_task.img.name is not None:
                msg.attach(support_task.img.name, support_task.img.read())

            support_task_send = threading.Thread(target=msg.send)
            support_task_send.start()
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )


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


@method_decorator(csrf_exempt, name='dispatch')
class CryptoWallets(View):

    def post(self, request, **kwargs):
        currency_id = request.POST.get('currency_id')
        if currency_id is None:
            return JsonResponse({'success': False}, status=400)

        wallets = CryptoWallet.objects.filter(
            currency__id=currency_id
        ).prefetch_related(
            'blockchain', 'currency'
        ).annotate(
            blockchain_name=F('blockchain__blockchain_name')
        ).values(
            'blockchain_name', 'id',
        )

        return JsonResponse(
            {
                'success': True,
                'wallets': list(wallets)
            },
            safe=False,
            status=200
        )


def clear_temp_data(request):
    try:
        del request.session['current_sub_id']
    except KeyError:
        pass

    try:
        del request.session['current_offer_id']
    except KeyError:
        pass


