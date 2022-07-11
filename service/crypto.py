import requests


BINANCE_PRICES_API_URL = 'https://api.binance.com/api/v3/ticker/price'

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
    return CRYPTO_WALLETS[currency][blockchain]


def get_crypto_amount(cyrrency, amount):
    price_url = f'{BINANCE_PRICES_API_URL}?symbol={cyrrency}USDT'
    data = requests.get(price_url).json()
    crypto_amount = float(amount) / float(data['price'])
    return str(round(crypto_amount, 8))+' '+cyrrency
