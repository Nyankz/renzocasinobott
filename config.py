import os

# Токен бота
BOT_TOKEN = "7684111869:AAFMIAEfA9oLaknk5GUYBDrpgr1uk-HNLZU"

# Криптовалютный API
CRYPTO_API_TOKEN = "424273:AAYYuBI8tIGsDIWMngAZgkHxzrX43mMQIYj"
CRYPTO_API_URL = "https://api.cryptobot.to/api"

# ID администраторов
ADMIN_IDS = [764515145]  # Замените на ваши ID

# Настройки игр
GAMES_CONFIG = {
    'slots': {
        'min_bet': 10,
        'max_bet': 10000,
        'win_multiplier': 5
    },
    'roulette': {
        'min_bet': 10,
        'max_bet': 10000
    },
    'dice': {
        'min_bet': 10,
        'max_bet': 10000,
        'win_multiplier': 2
    }
}

# Настройки комиссий
WITHDRAWAL_FEE = 0.05  # 5%
MIN_WITHDRAWAL = 100

# Реферальная система
REFERRAL_BONUS = 0.1  # 10%

# Канал для трансляции игр
GAMES_CHANNEL_ID = "@your_games_channel"  # Замените на ID или username вашего канала

# Поддерживаемые криптовалюты
SUPPORTED_CURRENCIES = {
    'BTC': {'name': '₿ Bitcoin', 'min_amount': 0.0001},
    'ETH': {'name': 'Ξ Ethereum', 'min_amount': 0.001},
    'USDT': {'name': '₮ USDT', 'min_amount': 1},
    'TON': {'name': '💎 TON', 'min_amount': 0.1},
    'BNB': {'name': '🟡 BNB', 'min_amount': 0.001},
    'USDC': {'name': '🔵 USDC', 'min_amount': 1},
    'LTC': {'name': 'Ł Litecoin', 'min_amount': 0.001}
}

# Курсы валют (примерные, для конвертации в рубли)
EXCHANGE_RATES = {
    'BTC': 2800000,  # 1 BTC = 2,800,000 RUB
    'ETH': 200000,   # 1 ETH = 200,000 RUB
    'USDT': 90,      # 1 USDT = 90 RUB
    'TON': 180,      # 1 TON = 180 RUB
    'BNB': 25000,    # 1 BNB = 25,000 RUB
    'USDC': 90,      # 1 USDC = 90 RUB
    'LTC': 7000      # 1 LTC = 7,000 RUB
}