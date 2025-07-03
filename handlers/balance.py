from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_user_balance, get_user_transactions, get_user
from config import MIN_WITHDRAWAL, WITHDRAWAL_FEE

router = Router()

@router.callback_query(F.data == "balance")
async def balance_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = get_user_balance(user_id)
    user = get_user(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit"),
            InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton(text="📊 История", callback_data="transactions"),
            InlineKeyboardButton(text="📈 Статистика", callback_data="stats")
        ],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    
    balance_text = (
        f"💰 <b>Ваш баланс</b>\n\n"
        f"💵 Основной: {balance['main']:.2f} ₽\n"
        f"🎁 Бонусный: {balance['bonus']:.2f} ₽\n"
        f"💎 Общий: {balance['main'] + balance['bonus']:.2f} ₽\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"🎮 Игр сыграно: {user['games_played']}\n"
        f"💰 Всего поставлено: {user['total_wagered']:.2f} ₽\n"
        f"📥 Пополнено: {user['total_deposited']:.2f} ₽\n"
        f"📤 Выведено: {user['total_withdrawn']:.2f} ₽"
    )
    
    await callback.message.edit_text(balance_text, reply_markup=keyboard)

@router.callback_query(F.data == "deposit")
async def deposit_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="₿ Bitcoin", callback_data="deposit_BTC"),
            InlineKeyboardButton(text="Ξ Ethereum", callback_data="deposit_ETH")
        ],
        [
            InlineKeyboardButton(text="₮ USDT", callback_data="deposit_USDT"),
            InlineKeyboardButton(text="Ł Litecoin", callback_data="deposit_LTC")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="balance")]
    ])
    
    await callback.message.edit_text(
        "💳 <b>Пополнение баланса</b>\n\n"
        "Выберите криптовалюту для пополнения:\n\n"
        "⚡ Средства поступят автоматически после подтверждения в сети\n"
        "🔒 Все транзакции защищены и анонимны",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("deposit_"))
async def show_deposit_address(callback: CallbackQuery):
    currency = callback.data.split("_")[1]
    address = CRYPTO_ADDRESSES.get(currency)
    
    if not address:
        await callback.answer("❌ Адрес не найден!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="deposit")]
    ])
    
    currency_names = {
        'BTC': '₿ Bitcoin',
        'ETH': 'Ξ Ethereum', 
        'USDT': '₮ USDT',
        'LTC': 'Ł Litecoin'
    }
    
    deposit_text = (
        f"💳 <b>Пополнение {currency_names[currency]}</b>\n\n"
        f"📋 <b>Адрес для пополнения:</b>\n"
        f"<code>{address}</code>\n\n"
        f"⚠️ <b>Важно:</b>\n"
        f"• Отправляйте только {currency} на этот адрес\n"
        f"• Минимальная сумма: эквивалент 100 ₽\n"
        f"• Средства зачисляются после 1 подтверждения\n"
        f"• Обычно это занимает 10-30 минут\n\n"
        f"💡 Скопируйте адрес и отправьте на него криптовалюту"
    )
    
    await callback.message.edit_text(deposit_text, reply_markup=keyboard)

@router.callback_query(F.data == "withdraw")
async def withdraw_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = get_user_balance(user_id)
    
    if balance['main'] < MIN_WITHDRAWAL:
        await callback.answer(f"❌ Минимальная сумма для вывода: {MIN_WITHDRAWAL} ₽")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="₿ Bitcoin", callback_data="withdraw_BTC"),
            InlineKeyboardButton(text="Ξ Ethereum", callback_data="withdraw_ETH")
        ],
        [
            InlineKeyboardButton(text="₮ USDT", callback_data="withdraw_USDT"),
            InlineKeyboardButton(text="Ł Litecoin", callback_data="withdraw_LTC")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="balance")]
    ])
    
    fee_amount = balance['main'] * WITHDRAWAL_FEE
    after_fee = balance['main'] - fee_amount
    
    withdraw_text = (
        f"💸 <b>Вывод средств</b>\n\n"
        f"💰 Доступно для вывода: {balance['main']:.2f} ₽\n"
        f"💳 Комиссия: {WITHDRAWAL_FEE*100}% ({fee_amount:.2f} ₽)\n"
        f"💵 К получению: {after_fee:.2f} ₽\n\n"
        f"⚡ Выплаты обрабатываются в течение 24 часов\n"
        f"🔒 Минимальная сумма: {MIN_WITHDRAWAL} ₽\n\n"
        f"Выберите криптовалюту:"
    )
    
    await callback.message.edit_text(withdraw_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("withdraw_"))
async def process_withdraw(callback: CallbackQuery):
    currency = callback.data.split("_")[1]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="withdraw")]
    ])
    
    currency_names = {
        'BTC': '₿ Bitcoin',
        'ETH': 'Ξ Ethereum',
        'USDT': '₮ USDT', 
        'LTC': 'Ł Litecoin'
    }
    
    await callback.message.edit_text(
        f"💸 <b>Вывод {currency_names[currency]}</b>\n\n"
        f"📝 Напишите адрес кошелька для вывода {currency}\n\n"
        f"⚠️ <b>Внимание:</b>\n"
        f"• Проверьте адрес несколько раз\n"
        f"• Неверный адрес = потеря средств\n"
        f"• Мы не несем ответственность за ошибки в адресе",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "transactions")
async def show_transactions(callback: CallbackQuery):
    user_id = callback.from_user.id
    transactions = get_user_transactions(user_id, 10)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="balance")]
    ])
    
    if not transactions:
        await callback.message.edit_text(
            "📊 <b>История транзакций</b>\n\n"
            "У вас пока нет транзакций",
            reply_markup=keyboard
        )
        return
    
    transactions_text = "📊 <b>История транзакций</b>\n\n"
    
    for t in transactions[:10]:
        amount_str = f"+{t['amount']:.2f}" if t['amount'] > 0 else f"{t['amount']:.2f}"
        emoji = "💰" if t['amount'] > 0 else "💸"
        
        transactions_text += (
            f"{emoji} {amount_str} ₽ - {t['description']}\n"
            f"📅 {t['timestamp'][:16]}\n\n"
        )
    
    await callback.message.edit_text(transactions_text, reply_markup=keyboard)

@router.callback_query(F.data == "referrals")
async def referrals_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    
    referral_link = f"https://t.me/your_bot_username?start={user_id}"
    
    referrals_text = (
        f"👥 <b>Реферальная программа</b>\n\n"
        f"🎁 Получайте 10% с каждого пополнения рефералов!\n\n"
        f"🔗 <b>Ваша реферальная ссылка:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        f"📋 <b>Как это работает:</b>\n"
        f"• Поделитесь ссылкой с друзьями\n"
        f"• Они регистрируются по вашей ссылке\n"
        f"• Вы получаете 10% с их пополнений\n"
        f"• Бонусы начисляются на бонусный баланс\n\n"
        f"💡 Чем больше рефералов, тем больше доход!"
    )
    
    await callback.message.edit_text(referrals_text, reply_markup=keyboard)

@router.callback_query(F.data == "profile")
async def profile_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    balance = get_user_balance(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    
    # Вычисляем прибыль/убыток
    profit_loss = balance['main'] + balance['bonus'] + user['total_withdrawn'] - user['total_deposited']
    profit_emoji = "📈" if profit_loss >= 0 else "📉"
    
    profile_text = (
        f"📊 <b>Профиль игрока</b>\n\n"
        f"👤 {user['full_name']}\n"
        f"🆔 ID: {user['user_id']}\n"
        f"📅 Регистрация: {user['registration_date'][:10]}\n\n"
        f"💰 <b>Балансы:</b>\n"
        f"💵 Основной: {balance['main']:.2f} ₽\n"
        f"🎁 Бонусный: {balance['bonus']:.2f} ₽\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"🎮 Игр сыграно: {user['games_played']}\n"
        f"💰 Всего поставлено: {user['total_wagered']:.2f} ₽\n"
        f"📥 Пополнено: {user['total_deposited']:.2f} ₽\n"
        f"📤 Выведено: {user['total_withdrawn']:.2f} ₽\n"
        f"{profit_emoji} Прибыль/Убыток: {profit_loss:+.2f} ₽"
    )
    
    await callback.message.edit_text(profile_text, reply_markup=keyboard)
