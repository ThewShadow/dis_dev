import requests
import qrcode
from config import settings
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


def gen_crypto_pay_link(currency, blockchain):
    try:
        return CRYPTO_WALLETS[currency][blockchain]
    except KeyError:
        return None



def get_crypto_amount(currency, amount):
    price_url = f'{BINANCE_PRICES_API_URL}?symbol={currency}USDT&interval=1m'
    data = requests.get(price_url).json()
    crypto_amount = float(amount) / float(data[-1][4])

    return str(round(crypto_amount, 8))+' '+currency



def gen_qrcode(payment_code):

    fileName = str(settings.BASE_DIR) + '/static/img/QR/' + str(payment_code) + '.jpg'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(payment_code)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(fileName) #write qrcode encoded data to the image file.

    return fileName.replace(str(settings.BASE_DIR), '')