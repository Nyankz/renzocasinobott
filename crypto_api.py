import aiohttp
import asyncio
import hashlib
import hmac
import time
from typing import Dict, Optional, List
from config import CRYPTO_API_TOKEN, CRYPTO_API_URL, EXCHANGE_RATES

class CryptoAPI:
    def __init__(self):
        self.token = CRYPTO_API_TOKEN
        self.base_url = CRYPTO_API_URL
        
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Выполнить запрос к API"""
        headers = {
            'Crypto-Pay-API-Token': self.token,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                if method == 'GET':
                    async with session.get(url, headers=headers, params=data) as response:
                        return await response.json()
                elif method == 'POST':
                    async with session.post(url, headers=headers, json=data) as response:
                        return await response.json()
            except Exception as e:
                print(f"Ошибка API запроса: {e}")
                return {'ok': False, 'error': str(e)}
    
    async def get_me(self) -> Dict:
        """Получить информацию о приложении"""
        return await self._make_request('GET', 'getMe')
    
    async def get_balance(self) -> Dict:
        """Получить баланс"""
        return await self._make_request('GET', 'getBalance')
    
    async def get_currencies(self) -> Dict:
        """Получить список поддерживаемых валют"""
        return await self._make_request('GET', 'getCurrencies')
    
    async def get_exchange_rates(self) -> Dict:
        """Получить курсы валют"""
        return await self._make_request('GET', 'getExchangeRates')
    
    async def create_invoice(self, amount: float, currency: str, description: str = "", 
                           payload: str = "", expires_in: int = 3600) -> Dict:
        """Создать счет для оплаты"""
        data = {
            'currency_type': 'crypto',
            'asset': currency,
            'amount': str(amount),
            'description': description,
            'payload': payload,
            'expires_in': expires_in
        }
        
        return await self._make_request('POST', 'createInvoice', data)
    
    async def get_invoices(self, invoice_ids: List[int] = None, status: str = None, 
                          offset: int = 0, count: int = 100) -> Dict:
        """Получить список счетов"""
        data = {
            'offset': offset,
            'count': count
        }
        
        if invoice_ids:
            data['invoice_ids'] = invoice_ids
        if status:
            data['status'] = status
            
        return await self._make_request('GET', 'getInvoices', data)
    
    async def create_check(self, amount: float, currency: str, pin_to_user_id: int = None) -> Dict:
        """Создать чек для вывода средств"""
        data = {
            'currency_type': 'crypto',
            'asset': currency,
            'amount': str(amount)
        }
        
        if pin_to_user_id:
            data['pin_to_user_id'] = pin_to_user_id
            
        return await self._make_request('POST', 'createCheck', data)
    
    async def delete_check(self, check_id: int) -> Dict:
        """Удалить чек"""
        data = {'check_id': check_id}
        return await self._make_request('POST', 'deleteCheck', data)
    
    async def get_checks(self, status: str = None, offset: int = 0, count: int = 100) -> Dict:
        """Получить список чеков"""
        data = {
            'offset': offset,
            'count': count
        }
        
        if status:
            data['status'] = status
            
        return await self._make_request('GET', 'getChecks', data)
    
    def convert_to_rub(self, amount: float, currency: str) -> float:
        """Конвертировать криптовалюту в рубли"""
        rate = EXCHANGE_RATES.get(currency, 1)
        return amount * rate
    
    def convert_from_rub(self, rub_amount: float, currency: str) -> float:
        """Конвертировать рубли в криптовалюту"""
        rate = EXCHANGE_RATES.get(currency, 1)
        return rub_amount / rate

# Глобальный экземпляр API
crypto_api = CryptoAPI()