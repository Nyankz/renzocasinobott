from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user_balance, get_user_transactions, get_user
from config import MIN_WITHDRAWAL, WITHDRAWAL_FEE
from crypto_api import create_invoice

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
        "⚡ После оплаты сумма поступит автоматически\n"
        "🔒 Все транзакции защищены и анонимны",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("deposit_"))
async def show_deposit_invoice(callback: CallbackQuery):
    currency = callback.data.split("_")[1]
    user_id = callback.from_user.id

    invoice = await 
create_invoice(user_id, currency)
    if not invoice or "pay_url" not in invoice:
    await 
        callback.answer("Ошибка при создании чека!", show_alert=True)
    return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Перейти к оплате", url=invoice["pay_url"])],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="deposit")]
    ])

    await callback.message.edit_text(
        f"💳 <b>Пополнение {currency}</b>\n\n"
        f"🔗 Чек успешно создан. Перейдите по кнопке ниже для оплаты.\n"
        f"⚠️ Минимальная сумма — 0.1 USD",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "withdraw")
async def withdraw_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = get_user_balance(user_id)

    if balance['main'] < MIN_WITHDRAWAL:
        await callback.answer(f"❌ Минимальная сумма для вывода: {MIN_WITHDRAWAL} ₽")
        return

    fee_amount = balance['main'] * WITHDRAWAL_FEE
    after_fee = balance['main'] - fee_amount

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

    await callback.message.edit_text(
        f"💸 <b>Вывод {currency}</b>\n\n"
        f"📝 Отправьте адрес кошелька для получения средств\n"
        f"⚠️ Будьте внимательны: ошибки в адресе могут привести к потере средств",
        reply_markup=keyboard
    )
