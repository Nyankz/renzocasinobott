# crypto_api.py

import aiohttp
from config import CRYPTO_API_TOKEN


async def create_invoice(user_id: int, amount: float, currency: str = "USDT"):
    url = "https://api.cryptobot.to/api/createInvoice"
    
    headers = {
        "Crypto-Pay-API-Token": CRYPTO_API_TOKEN,
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": amount,
        "currency": currency,
        "lifetime": 300,
        "hidden_message": f"user_id:{user_id}",
        "paid_btn_name": "openBot",
        "paid_btn_url": f"https://t.me/renzocasinobot"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            if data.get("ok"):
                return data["result"]["pay_url"]
            return None