import os.path
from main.models import Blockchain, CryptoWallet, Currency
import requests
import qrcode
from config import settings
import logging
from main.models import Subscription

logger = logging.getLogger('main')

BINANCE_PRICES_API_URL = 'https://api.binance.com/api/v1/klines'
#
# CRYPTO_WALLETS = {
#     'Bitcoin': {
#         'Blockchain BTC network': '3PGgmpAxfzDSyPAGPqdL2oe5yS78UytENU',
#         'Blockchain Solana network': 'miGrDEXrVU2sn276HxqxHvua4kBFn6s9R2adVKnSbmN',
#         'Blockchain BSC network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183'
#     },
#     'Ethereum': {
#         'Blockchain ETH network': '0x989e4Aed8433ac16bbc81aD113426ba8c2f2B299',
#         'Blockchain Solana network': 'miGrDEXrVU2sn276HxqxHvua4kBFn6s9R2adVKnSbmN',
#         'Blockchain BSC network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183'
#     },
#     'USDT': {
#         'Blockchain ERC20 network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183',
#         'Blockchain Solana network': 'miGrDEXrVU2sn276HxqxHvua4kBFn6s9R2adVKnSbmN',
#         'Blockchain BSC network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183'
#     },
# }
#
#
# def gen_pay_link(currency, blockchain):
#     try:
#         return CRYPTO_WALLETS[currency][blockchain]
#     except KeyError:
#         logger.error(f'Crypto wallet not found, args: {currency}, {blackchain}')
#         return None
#
#
#
# def get_amount(currency, amount):
#     price_url = f'{BINANCE_PRICES_API_URL}?symbol={currency}USDT&interval=1m'
#     response = requests.get(price_url)
#
#     logging.debug(f'Binance price response: {str(response)}')
#
#     try:
#         prises = response.json()
#     except requests.RequestsJSONDecodeError:
#         prises = []
#         logger.error('Price parsing error')
#
#     try:
#         price = prises[-1][4]
#     except IndexError:
#         price = 0
#         logger.error('Price parsing error')
#
#     try:
#         crypto_amount = float(amount) / float(price)
#     except ZeroDivisionError:
#         crypto_amount = 0
#         logger.error(f'Crypto amount not calculated. price: {price}, amount: {amount}')
#
#     return str(round(crypto_amount, 8))+' '+currency
#
#
#
# def gen_qrcode(payment_code):
#
#     if not isinstance(payment_code, str)\
#             or not payment_code:
#         return None
#
#     file_name = str(settings.BASE_DIR) \
#                + '/static/img/QR/' \
#                + str(payment_code) + '.jpg'
#
#     if not os.path.exists(file_name):
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#
#         qr.add_data(payment_code)
#         qr.make(fit=True)
#
#         img = qr.make_image()
#         img.save(file_name)
#
#     return file_name.replace(str(settings.BASE_DIR), '')
#


class CryptoConverter():

    ALLOW_CONVERT_CODES = ['BTC', 'ETH']

    def __init__(self, blockchain, currency):
        self.blockchain = blockchain
        self.currency = currency
        self.rates_url = self.__get_rates_url_by_currency()
        self.crypto_rates = self.__download_rates()

    def convert(self, price):
        if self.currency.code.upper() not in self.ALLOW_CONVERT_CODES:
            return price
        else:
            rate = self.__get_rate()
            if rate == 0:
               raise ValueError('price n')
            try:
                converted_price = float(price) / float(rate)
            except ZeroDivisionError:
                converted_price = 0
                logger.error(f'Crypto amount not calculated. rate: {rate}, price: {price}')
        return round(converted_price, 8)

    def __get_rate(self):
        try:
            return self.crypto_rates[-1][4]
        except IndexError:
            logger.error('Price not found by prices[-1][4]')
            return 0

    def __get_rates_url_by_currency(self):
        if not self.currency:
            raise ValueError('currency must be object <Currency>')
        return f'{BINANCE_PRICES_API_URL}?symbol={self.currency.code}USDT&interval=1m'

    def __download_rates(self):
        if not self.rates_url:
            raise ValueError('price_url must be string')

        response = requests.get(self.rates_url)
        logging.debug(f'Binance price response: {str(response)}')
        try:
            return response.json()
        except requests.RequestsJSONDecodeError as e:
            logger.error(f'Price parsing fail.\n error: {e}')
            return []


class CryptoPaymentGenerator:

    def __init__(self, sub_id, wallet_id):

        self.qr_generator = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        self.price = self.get_subscription_price(sub_id)
        self.wallet = self.get_wallet(wallet_id)
        self.price_converter = CryptoConverter(self.wallet.blockchain, self.wallet.currency)

    def get_payment_data(self):
       return {
            'paycode': self.get_paycode(),
            'qrcode': self.get_qrcode(self.get_paycode()),
            'price':self.price_converter.convert(self.price),
            'blockchain': self.wallet.blockchain.blockchain_name,
            'currency': self.wallet.currency.code
       }

    def get_paycode(self):
        if self.wallet:
            return self.wallet.paycode
        else:
            raise ValueError('Wallet not found')

    def get_qrcode(self, payment_code):
        payment_code = self.get_paycode()
        if not isinstance(payment_code, str):
            raise ValueError('payment_code is not string')
        if not len(payment_code.strip()):
            raise ValueError('payment_code is empty')

        base_dir = str(settings.BASE_DIR)
        file_name = payment_code
        file_path = ''.join([base_dir, '/static/img/QR/', file_name, '.jpg'])
        web_path = file_path.replace(base_dir, '')

        if not os.path.exists(file_path):
            self.__make_qrcode(payment_code, file_path)
        return web_path

    def __make_qrcode(self, payment_code, file_path):
        QR = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,
        )
        QR.add_data(payment_code)
        QR.make(fit=True)
        QR.make_image().save(file_path)

    def get_wallet(self, wallet_id):
        return CryptoWallet.objects.filter(id=wallet_id).prefetch_related('blockchain', 'currency').first()
    def get_subscription_price(self, sub_id):
        try:
            return Subscription.objects.prefetch_related('offer').get(id=sub_id).offer.price
        except IndexError:
            return 0