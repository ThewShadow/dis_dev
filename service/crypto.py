import os.path

import requests
import qrcode
from config import settings
import logging

logger = logging.getLogger('main')

BINANCE_PRICES_API_URL = 'https://api.binance.com/api/v1/klines'

CRYPTO_WALLETS = {
    'Bitcoin': {
        'Blockchain BTC network': '3PGgmpAxfzDSyPAGPqdL2oe5yS78UytENU',
        'Blockchain Solana network': 'miGrDEXrVU2sn276HxqxHvua4kBFn6s9R2adVKnSbmN',
        'Blockchain BSC network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183'
    },
    'Ethereum': {
        'Blockchain ETH network': '0x989e4Aed8433ac16bbc81aD113426ba8c2f2B299',
        'Blockchain Solana network': 'miGrDEXrVU2sn276HxqxHvua4kBFn6s9R2adVKnSbmN',
        'Blockchain BSC network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183'
    },
    'USDT': {
        'Blockchain ERC20 network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183',
        'Blockchain Solana network': 'miGrDEXrVU2sn276HxqxHvua4kBFn6s9R2adVKnSbmN',
        'Blockchain BSC network': '0x080E1038AacBB32C52816FCD6BED1A7b7E3d8183'
    },
}


def gen_pay_link(currency, blockchain):
    try:
        return CRYPTO_WALLETS[currency][blockchain]
    except KeyError:
        logger.error(f'Crypto wallet not found, args: {currency}, {blackchain}')
        return None



def get_amount(currency, amount):
    price_url = f'{BINANCE_PRICES_API_URL}?symbol={currency}USDT&interval=1m'
    response = requests.get(price_url)

    logging.debug(f'Binance price response: {str(response)}')

    try:
        prises = response.json()
    except requests.RequestsJSONDecodeError:
        prises = []
        logger.error('Price parsing error')

    try:
        price = prises[-1][4]
    except IndexError:
        price = 0
        logger.error('Price parsing error')

    try:
        crypto_amount = float(amount) / float(price)
    except ZeroDivisionError:
        crypto_amount = 0
        logger.error(f'Crypto amount not calculated. price: {price}, amount: {amount}')

    return str(round(crypto_amount, 8))+' '+currency



def gen_qrcode(payment_code):

    if not isinstance(payment_code, str)\
            or not payment_code:
        return None

    file_name = str(settings.BASE_DIR) \
               + '/static/img/QR/' \
               + str(payment_code) + '.jpg'

    if not os.path.exists(file_name):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(payment_code)
        qr.make(fit=True)

        img = qr.make_image()
        img.save(file_name)

    return file_name.replace(str(settings.BASE_DIR), '')