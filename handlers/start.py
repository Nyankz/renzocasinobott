from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from database import get_user, create_user, get_user_balance

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name
    
    # Проверяем реферальный код
    referrer_id = None
    if message.text and len(message.text.split()) > 1:
        try:
            referrer_id = int(message.text.split()[1])
        except ValueError:
            pass
    
    # Проверяем, есть ли пользователь в базе
    user = get_user(user_id)
    if not user:
        create_user(user_id, username, full_name, referrer_id)
        
        # Если есть реферер, начисляем бонус
        if referrer_id:
            from database import update_balance, add_transaction
            from config import REFERRAL_BONUS
            
            # Проверяем, что реферер существует
            referrer = get_user(referrer_id)
            if referrer:
                bonus_amount = 100 * REFERRAL_BONUS  # 10% от 100 рублей
                update_balance(referrer_id, bonus_amount, 'bonus')
                add_transaction(referrer_id, bonus_amount, 'referral_bonus', f'Реферальный бонус за пользователя {full_name}')
    
    balance = get_user_balance(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎮 Игры", callback_data="games"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ],
        [
            InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit"),
            InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"),
            InlineKeyboardButton(text="📊 Профиль", callback_data="profile")
        ]
    ])
    
    welcome_text = (
        f"🎰 <b>Добро пожаловать в Криптовалютное Казино!</b>\n\n"
        f"👤 {full_name}\n"
        f"💰 Основной баланс: {balance['main']:.2f} ₽\n"
        f"🎁 Бонусный баланс: {balance['bonus']:.2f} ₽\n\n"
        f"🎮 Доступные игры:\n"
        f"• 🎯 Рулетка с трансляцией\n"
        f"• 🎰 Слоты\n"
        f"• 🎲 Кости\n\n"
        f"💎 Пополнение через криптовалюты\n"
        f"🚀 Мгновенные выплаты"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

@router.callback_query(F.data == "games")
async def games_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎰 Слоты", callback_data="slots"),
            InlineKeyboardButton(text="🎯 Рулетка", callback_data="roulette")
        ],
        [
            InlineKeyboardButton(text="🎲 Кости", callback_data="dice"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        "🎮 <b>Игровое меню</b>\n\n"
        "Выберите игру:",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    balance = get_user_balance(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎮 Игры", callback_data="games"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ],
        [
            InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit"),
            InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"),
            InlineKeyboardButton(text="📊 Профиль", callback_data="profile")
        ]
    ])
    
    welcome_text = (
        f"🎰 <b>Криптовалютное Казино</b>\n\n"
        f"👤 {full_name}\n"
        f"💰 Основной баланс: {balance['main']:.2f} ₽\n"
        f"🎁 Бонусный баланс: {balance['bonus']:.2f} ₽\n\n"
        f"🎮 Доступные игры:\n"
        f"• 🎯 Рулетка с трансляцией\n"
        f"• 🎰 Слоты\n"
        f"• 🎲 Кости\n\n"
        f"💎 Пополнение через криптовалюты\n"
        f"🚀 Мгновенные выплаты"
    )
    
    await callback.message.edit_text(welcome_text, reply_markup=keyboard)

@router.message(Command("menu"))
async def menu_command(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    balance = get_user_balance(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎮 Игры", callback_data="games"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ],
        [
            InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit"),
            InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"),
            InlineKeyboardButton(text="📊 Профиль", callback_data="profile")
        ]
    ])
    
    welcome_text = (
        f"🎰 <b>Криптовалютное Казино</b>\n\n"
        f"👤 {full_name}\n"
        f"💰 Основной баланс: {balance['main']:.2f} ₽\n"
        f"🎁 Бонусный баланс: {balance['bonus']:.2f} ₽\n\n"
        f"🎮 Доступные игры:\n"
        f"• 🎯 Рулетка с трансляцией\n"
        f"• 🎰 Слоты\n"
        f"• 🎲 Кости\n\n"
        f"💎 Пополнение через криптовалюты\n"
        f"🚀 Мгновенные выплаты"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)