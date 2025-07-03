from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_all_users, get_bot_stats, update_balance, add_transaction, get_user
from config import ADMIN_IDS

router = Router()

def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    stats = get_bot_stats()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="💰 Управление балансом", callback_data="admin_balance"),
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")
        ]
    ])
    
    admin_text = (
        f"🔧 <b>Панель администратора</b>\n\n"
        f"📊 <b>Быстрая статистика:</b>\n"
        f"👥 Пользователей: {stats['total_users']}\n"
        f"💰 Общий баланс: {stats['total_balance']:.2f} ₽\n"
        f"🎮 Игр сыграно: {stats['total_games']}\n"
        f"💸 Общие ставки: {stats['total_wagered']:.2f} ₽"
    )
    
    await message.answer(admin_text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав!")
        return
    
    stats = get_bot_stats()
    users = get_all_users()
    
    # Топ игроков по балансу
    top_balance = sorted(users, key=lambda x: x['main_balance'] + x['bonus_balance'], reverse=True)[:5]
    
    # Топ игроков по ставкам
    top_wagered = sorted(users, key=lambda x: x['total_wagered'], reverse=True)[:5]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_back")]
    ])
    
    stats_text = (
        f"📊 <b>Подробная статистика</b>\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"💰 Общий баланс: {stats['total_balance']:.2f} ₽\n"
        f"🎮 Игр сыграно: {stats['total_games']}\n"
        f"💸 Общие ставки: {stats['total_wagered']:.2f} ₽\n\n"
        f"🏆 <b>Топ по балансу:</b>\n"
    )
    
    for i, user in enumerate(top_balance, 1):
        total_balance = user['main_balance'] + user['bonus_balance']
        stats_text += f"{i}. {user['full_name']}: {total_balance:.2f} ₽\n"
    
    stats_text += f"\n💎 <b>Топ по ставкам:</b>\n"
    
    for i, user in enumerate(top_wagered, 1):
        stats_text += f"{i}. {user['full_name']}: {user['total_wagered']:.2f} ₽\n"
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав!")
        return
    
    users = get_all_users()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_back")]
    ])
    
    users_text = f"👥 <b>Список пользователей</b> (последние 10)\n\n"
    
    for user in users[:10]:
        total_balance = user['main_balance'] + user['bonus_balance']
        users_text += (
            f"👤 {user['full_name']}\n"
            f"🆔 {user['user_id']}\n"
            f"💰 {total_balance:.2f} ₽\n"
            f"🎮 {user['games_played']} игр\n\n"
        )
    
    await callback.message.edit_text(users_text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_balance")
async def admin_balance_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(
        "💰 <b>Управление балансом</b>\n\n"
        "Отправьте команду в формате:\n"
        "<code>/setbalance USER_ID AMOUNT</code>\n\n"
        "Например:\n"
        "<code>/setbalance 123456789 1000</code>\n\n"
        "Для добавления к балансу используйте:\n"
        "<code>/addbalance USER_ID AMOUNT</code>",
        reply_markup=keyboard
    )

@router.message(Command("setbalance"))
async def set_balance_command(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("❌ Неверный формат! Используйте: /setbalance USER_ID AMOUNT")
            return
        
        user_id = int(parts[1])
        amount = float(parts[2])
        
        user = get_user(user_id)
        if not user:
            await message.answer("❌ Пользователь не найден!")
            return
        
        # Устанавливаем новый баланс
        current_balance = user['main_balance']
        difference = amount - current_balance
        
        update_balance(user_id, difference, 'main')
        add_transaction(user_id, difference, 'admin_adjustment', f'Корректировка баланса администратором')
        
        await message.answer(
            f"✅ Баланс пользователя {user['full_name']} установлен на {amount:.2f} ₽"
        )
        
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат! Используйте: /setbalance USER_ID AMOUNT")

@router.message(Command("addbalance"))
async def add_balance_command(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("❌ Неверный формат! Используйте: /addbalance USER_ID AMOUNT")
            return
        
        user_id = int(parts[1])
        amount = float(parts[2])
        
        user = get_user(user_id)
        if not user:
            await message.answer("❌ Пользователь не найден!")
            return
        
        update_balance(user_id, amount, 'main')
        add_transaction(user_id, amount, 'admin_bonus', f'Бонус от администратора')
        
        new_balance = user['main_balance'] + amount
        
        await message.answer(
            f"✅ К балансу пользователя {user['full_name']} добавлено {amount:.2f} ₽\n"
            f"Новый баланс: {new_balance:.2f} ₽"
        )
        
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат! Используйте: /addbalance USER_ID AMOUNT")

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав!")
        return
    
    stats = get_bot_stats()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="💰 Управление балансом", callback_data="admin_balance"),
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")
        ]
    ])
    
    admin_text = (
        f"🔧 <b>Панель администратора</b>\n\n"
        f"📊 <b>Быстрая статистика:</b>\n"
        f"👥 Пользователей: {stats['total_users']}\n"
        f"💰 Общий баланс: {stats['total_balance']:.2f} ₽\n"
        f"🎮 Игр сыграно: {stats['total_games']}\n"
        f"💸 Общие ставки: {stats['total_wagered']:.2f} ₽"
    )
    
    await callback.message.edit_text(admin_text, reply_markup=keyboard)